import ctypes
import inspect
import json
import multiprocessing
import os
import time
from io import StringIO
from multiprocessing import Queue
from pathlib import Path
from pprint import pformat
from subprocess import call
from unittest.mock import Mock, patch

import coverage
import signal_disabler

from bok_choy.browser import BROWSERS
from bok_choy.page_object import PageObject, unguarded
from bok_choy.promise import EmptyPromise, BrokenPromise, Promise
from bok_choy.web_app_test import WebAppTest
from ddt import ddt, data
from django.conf import settings
from django.contrib.auth.models import AnonymousUser
from django.core import management
from django.core.management import call_command
from django.db import connections
from django.forms import CheckboxInput, RadioSelect
from django.test import LiveServerTestCase, override_settings, tag
from django.test.runner import DiscoverRunner, ParallelTestSuite
from django.urls import reverse
from needle.driver import NeedleFirefox
from pyvirtualdisplay import Display
from rest_framework.exceptions import PermissionDenied
from rest_framework.generics import GenericAPIView
from rest_framework.test import APITestCase as BaseAPITestCase, APIRequestFactory
from seleniumrequests import RequestMixin

from apps.profiles.models import User

MIDDLEWARE = ['apps.lib.test_resources.DisableCSRF'] + settings.MIDDLEWARE


@tag('e2e')
@override_settings(MIDDLEWARE=MIDDLEWARE)
class BaseWebAppTest(LiveServerTestCase, WebAppTest):
    """
    Inherits from WebAppTest and LiveServerTestCase in order to have
    a live server to test against while running the bok_choy tests
    """

    def setUp(self):
        """
        Sets an environment variable with the value of the live server URL
        so that PageObject subclasses can pull this variable out and add it to their
        defined urls
        """
        # Monkey patch the definitions list to get our custom driver.
        BROWSERS['firefox'] = FFRequestsWebDriver
        if settings.HIDE_TEST_BROWSER:
            # Note: This only works on Linux VMs.
            self.display = Display(visible=0, size=(1024, 768))
            self.display.start()
        else:
            self.display = None
        os.environ['LIVE_SERVER_URL'] = self.live_server_url
        os.environ['SCREENSHOT_DIR'] = os.path.join(settings.BACKEND_ROOT, 'conf', 'logs')
        os.environ['SELENIUM_DRIVER_LOG_DIR'] = os.environ['SCREENSHOT_DIR']
        super(BaseWebAppTest, self).setUp()
        if not hasattr(self.server_thread, '_children'):
            self.server_thread._children = {}

    def tearDown(self):
        if settings.HIDE_TEST_BROWSER:
            self.display.stop()
        super(BaseWebAppTest, self).tearDown()

    def login(self, user, password='Test'):
        self.browser.request(
            'POST', self.live_server_url + '/api/profiles/v1/login/', data={'email': user.email, 'password': password}
        )


class BaseTestPage(PageObject):
    """
    Base class for all the pages class
    """
    _base_url = '/'

    # Used when making subqueries.
    block_id = None

    def __init__(self, browser, block_id=None):
        if block_id is not None:
            self.block_id = block_id
        super().__init__(browser)

    def is_browser_on_page(self):
        if self.block_id is None:
            return super().is_browser_on_page()
        return self.q().present

    @property
    def url(self):
        return os.environ["LIVE_SERVER_URL"] + self._base_url

    @property
    def messages(self):
        messages = {'success': [], 'warning': [], 'error': []}
        for key, value in messages.items():
            value.extend(element.text.strip(u'\xd7\n').strip() for element in self.q(css='.alert-{}'.format(key)))
        return messages

    @unguarded
    def q_toggle(self, root=False, *args, **kwargs):
        if root:
            return super().q(*args, **kwargs)
        else:
            return self.q(*args, **kwargs)

    @unguarded
    def q(self, *args, **kwargs):
        if not self.block_id:
            return super().q(*args, **kwargs)
        css = kwargs.pop('css', None)
        selector = "#{}".format(self.block_id)
        if css is not None:
            css = selector + ' ' + css
        else:
            css = selector
        return super().q(css=css, *args, **kwargs)

    def get_anchorlinks(self, url_name, anchor_args=None, use_resolver=False):
        """
        Used to get a list of anchor elements matching a specified url, designed to be used more
        commonly with no id attribute and no django named url.
        """
        anchor_args = anchor_args or []
        if use_resolver:
            url_name = reverse(url_name, args=anchor_args)
        element_selector = 'a[href^="' + url_name + '"]'
        self.wait_for_element_presence(element_selector, "anchor links are present")
        return self.q(css=element_selector)

    def get_anchorlink(self, url_name, anchor_args=None):
        """
        Used to get a single anchor element with the desired url on the target page.
        Designed to be used with an id attribute. and django named url.
        """
        anchor_args = anchor_args or []
        url = reverse(url_name, args=anchor_args)
        element_selector = 'a[href="' + url + '"]'
        self.wait_for_element_presence(element_selector, "anchor link is present")
        return self.q(css=element_selector)

    def wait_for_in_viewport(self, selector, description, timeout=60):
        """
        wait the process till given selector available on viewport
        """
        def check_viewport():
            self.wait_for_element_visibility(selector, description, timeout=timeout)
            element = self.q(css=selector)[0]
            location = element.location
            scroll_position_script = """
                var pageY;
                if (typeof(window.pageYOffset) == 'number') {
                    pageY = window.pageYOffset;
                } else {
                    pageY = document.documentElement.scrollTop;
                }
                return pageY;
            """
            y_offset = self.browser.execute_script(scroll_position_script)
            js_client_height = "return document.documentElement.clientHeight;"
            browser_height = self.browser.execute_script(js_client_height)
            return (location['y'] >= y_offset) and (location['y'] <= y_offset + browser_height)
        EmptyPromise(check_viewport, description, timeout=timeout).fulfill()

    @unguarded
    def wait_for_element_presence(self, element_selector, description, timeout=60, root=False):
        """
        Waits for element specified by `element_selector` to be present in DOM.

        Example usage:

        .. code:: python

            self.wait_for_element_presence('.submit', 'Submit Button is Present')

        Arguments:
            element_selector (str): css selector of the element.
            description (str): Description of the Promise, used in log messages.
            timeout (float): Maximum number of seconds to wait for the Promise to be satisfied before timing out
            root (bool): Whether or not to start the search at the root of the page rather than the current element.

        """
        self.wait_for(
            lambda: self.q_toggle(css=element_selector, root=root).present, description=description, timeout=timeout
        )

    @unguarded
    def wait_for_element_absence(self, element_selector, description, timeout=60, root=False):
        """
        Waits for element specified by `element_selector` until it disappears from DOM.

        Example usage:

        .. code:: python

            self.wait_for_element_absence('.submit', 'Submit Button is not Present')

        Arguments:
            element_selector (str): css selector of the element.
            description (str): Description of the Promise, used in log messages.
            timeout (float): Maximum number of seconds to wait for the Promise to be satisfied before timing out
            root (bool): Whether or not to start the search at the root of the page rather than the current element.

        """
        self.wait_for(
            lambda: not self.q_toggle(css=element_selector, root=root).present,
            description=description, timeout=timeout
        )

    @unguarded
    def wait_for_element_visibility(self, element_selector, description, timeout=60, root=False):
        """
        Waits for element specified by `element_selector` until it is displayed on web page.

        Example usage:

        .. code:: python

            self.wait_for_element_visibility('.submit', 'Submit Button is Visible')

        Arguments:
            element_selector (str): css selector of the element.
            description (str): Description of the Promise, used in log messages.
            timeout (float): Maximum number of seconds to wait for the Promise to be satisfied before timing out
            root (bool): Whether or not to start the search at the root of the page rather than the current element.

        """
        self.wait_for(
            lambda: self.q_toggle(css=element_selector, root=root).visible, description=description, timeout=timeout
        )

    @unguarded
    def wait_for_element_invisibility(self, element_selector, description, timeout=60, root=False):
        """
        Waits for element specified by `element_selector` until it disappears from the web page.

        Example usage:

        .. code:: python

            self.wait_for_element_invisibility('.submit', 'Submit Button Disappeared')

        Arguments:
            element_selector (str): css selector of the element.
            description (str): Description of the Promise, used in log messages.
            timeout (float): Maximum number of seconds to wait for the Promise to be satisfied before timing out
            root (bool): Whether or not to start the search at the root of the page rather than the current element.

        """
        self.wait_for(
            lambda: self.q_toggle(css=element_selector, root=root).invisible, description=description, timeout=timeout
        )

    @unguarded
    def scroll_to_element(self, element_selector, timeout=60, root=False):
        """
        Scrolls the browser such that the element specified appears at the top. Before scrolling, waits for
        the element to be present.

        Example usage:

        .. code:: python

            self.scroll_to_element('.far-down', 'Scroll to far-down')

        Arguments:
            element_selector (str): css selector of the element.
            timeout (float): Maximum number of seconds to wait for the element to be present on the
                page before timing out.
            root (bool): Whether or not to start the search at the root of the page rather than the current element.

        Raises: BrokenPromise if the element does not exist (and therefore scrolling to it is not possible)

        """
        # Ensure element exists
        msg = "Element '{element}' is present".format(element=element_selector)
        self.wait_for(lambda: self.q_toggle(css=element_selector, root=root).present, msg, timeout=timeout)

        # Obtain coordinates and use those for JavaScript call
        loc = super().q(self, css=element_selector).first.results[0].location
        self.browser.execute_script("window.scrollTo({x},{y})".format(x=loc['x'], y=loc['y']))


# noinspection PyPep8Naming
class memoized_property(property):
    pass


class CheckBox:
    """
    Base class for Checkbox element
    """
    def __init__(self, page, field_id):
        self.page = page
        self.field_id = field_id

    @property
    def checked(self):
        return self.page.q(css=self.field_id).attrs("value")[0]

    def click(self):
        """
        click event on checkbox
        """
        target = None
        for element in self.page.q(css=self.field_id + ', label[for={}]'.format(self.field_id.replace('#', '', 1))):
            if element.is_displayed():
                target = element
                break
        if not target:
            raise BrokenPromise(
                Promise(lambda: None, ("Checkbox ID {} can be clicked.".format(self.field_id)))
            )
        target.click()


class FieldHandlerMetaclass(type):
    """
    Metaclass for field handlers to automagically create getters/setters for fields.
    """

    @staticmethod
    def create_getter(field_id, field):
        if isinstance(field.widget, CheckboxInput):
            @memoized_property
            def checkbox_access(self):
                return CheckBox(self._page, field_id)
            return checkbox_access

        @memoized_property
        def field_access(self):
            return self._page.q(css=field_id).attrs("value")[0]
        return field_access

    @staticmethod
    def create_setter(field_access, field_id, field):
        @field_access.setter
        def field_access(self, value):
            if isinstance(field.widget, CheckboxInput):
                raise AttributeError("Cannot set a checkbox directly. You have to .click() it.")
            elif isinstance(field.widget, RadioSelect):
                radio = self._page.q(
                    css='[id^={id}][value="{value}"]'.format(id=field_id.replace('#', ''), value=value)
                )
                label_selector = 'label[for="{}"]'.format(radio[0].get_attribute('id'))
                self._page.wait_for_element_visibility(
                    label_selector, 'Waited for radio with value "{}" to be visible.'.format(value)
                )
                self._page.q(css=label_selector).click()
            else:
                self._page.q(css=field_id).fill(value)
        return field_access

    @classmethod
    def create_handles(mcs, field_id, field):
        handler = mcs.create_getter(field_id, field)
        handler = mcs.create_setter(handler, field_id, field)
        return handler

    def __new__(mcs, name, parents, dct):
        dct['_form'] = dct.pop('form')
        for field_name, field in dct['_form'].fields.items():
            prefix = dct['_form'].prefix
            if prefix:
                prefix += '-'
            else:
                prefix = ''
            field_id = "#id_{prefix}{field_name}".format(prefix=prefix, field_name=field_name)

            field_access = mcs.create_handles(field_id, field)

            dct[field_name] = field_access
        return super(FieldHandlerMetaclass, mcs).__new__(mcs, name, parents, dct)


class PageForm(PageObject):
    """
    Mixin to manage Forms
    """

    url = None

    def __init__(self, browser, form_id='', form=None):
        """
        init method for page form object
        """
        self.form_id = form_id
        # Can't set a variable directly in this instance because of
        # Python's attempt to keep us from affecting outside scope by accident.
        mutable_hack = {'form': form}

        if form:
            class FieldHandler(object):
                """
                Provides access to the fields on the form with getters and setters.
                """
                __metaclass__ = FieldHandlerMetaclass
                form = mutable_hack['form']

                def __init__(self, page):
                    self._page = page

            self.fields = FieldHandler(self)
        super(PageForm, self).__init__(browser)

    def is_browser_on_page(self):
        """
        check the requested page is loaded on current browser
        Returns: True or False

        """
        if not self.form_id:
            return self.q(css="form")
        return self.q(css='#{}'.format(self.form_id))

    def prefix(self, selector):
        if self.form_id:
            return "#{} {}".format(self.form_id, selector)
        return selector

    def submit(self):
        """
        Submits via the first button of type submit under the form ID.
        """
        self.q(css=self.prefix("input[type=submit]")).click()

    @property
    def errors(self):
        return [el.text for el in self.q(css=self.prefix('ul.errorlist >li'))]


class FixtureMixin(object):
    """
    Loads a file in tests that need fixtures.
    """
    def load_fixture(self, filename):
        directory = os.path.dirname(os.path.realpath(inspect.getfile(self.__class__)))
        filename = os.path.join(directory, 'fixtures', filename)
        with open(filename, 'r') as f:
            return f.read()

    def load_json_fixture(self, filename):
        """
        Loads a fixture as JSON
        """
        filename += '.json'
        return json.loads(self.load_fixture(filename))


class FFRequestsWebDriver(NeedleFirefox, RequestMixin):
    pass


def fixture_path(cls, name):
    return str(Path(inspect.getfile(cls)).parent / 'fixtures' / (name + '.json'))


class Fixtured(type):
    fixture_list = []

    @property
    def fixtures(cls):
        if not os.environ.get('REBUILD_FIXTURES', False):
            return [fixture_path(cls, name) for name in cls.fixture_list]
        return []


class FixtureBase(metaclass=Fixtured):
    fixtures_built = False

    @classmethod
    def save_fixture(cls, name):
        create_fixture(fixture_path(cls, name))
        cls.fixtures_built = True

    @property
    def rebuild_fixtures(self):
        return os.environ.get('REBUILD_FIXTURES', False) or self.fixtures_built

    def load_fixture(self, name):
        for db_name in self._databases_names(include_mirrors=False):
            call_command('loaddata', fixture_path(self.__class__, name), **{'verbosity': 0, 'database': db_name})


class APITestCase(BaseAPITestCase, FixtureBase):
    def login(self, user):
        result = self.client.login(email=user.email, password='Test')
        self.assertIs(result, True)

    @staticmethod
    def assertIDInList(member, container):
        if not isinstance(member, int):
            member = member.id
        for item in container:
            if item['id'] == member:
                break
        else:
            raise AssertionError("ID {} not found in: {}".format(
                member,
                '[' + ',\n'.join([pformat(item) for item in container]) + ']')
            )


_worker_id = 0


def _init_worker(counter):
    """
    Switch to databases dedicated to this worker.

    This helper lives at module-level because of the multiprocessing module's
    requirements.
    """
    global _worker_id

    with counter.get_lock():
        counter.value += 1
        _worker_id = counter.value

    for alias in connections:
        connection = connections[alias]
        settings_dict = connection.creation.get_test_db_clone_settings(str(_worker_id))
        # connection.settings_dict must be updated in place for changes to be
        # reflected in django.db.connections. If the following line assigned
        # connection.settings_dict = settings_dict, new threads would connect
        # to the default database instead of the appropriate clone.
        connection.settings_dict.update(settings_dict)
        connection.close()
    # Remove parent process reference, which won't be valid.
    try:
        del coverage.process_startup.coverage
    except AttributeError:
        pass
    coverage.process_startup()


def save_coverage(*_args):
    cov = getattr(coverage.process_startup, 'coverage', None)
    if not cov:
        return
    cov.stop()
    cov.save()


class CoveredParallelTestSuite(ParallelTestSuite):
    init_worker = _init_worker

    def run(self, result):
        """
        Distribute test cases across workers.

        Return an identifier of each test case with its result in order to use
        imap_unordered to show results as soon as they're available.

        To minimize pickling errors when getting results from workers:

        - pass back numeric indexes in self.subsuites instead of tests
        - make tracebacks picklable with tblib, if available

        Even with tblib, errors may still occur for dynamically created
        exception classes which cannot be unpickled.

        This function is nearly verbatim copied from upstream, but modified
        to make sure coverage is properly handled.
        """
        # noinspection PyTypeChecker
        counter = multiprocessing.Value(ctypes.c_int, 0)
        pool = multiprocessing.Pool(
            processes=self.processes,
            initializer=self.init_worker.__func__,
            initargs=[counter],
        )
        args = [
            (self.runner_class, index, subsuite, self.failfast)
            for index, subsuite in enumerate(self.subsuites)
        ]
        test_results = pool.imap_unordered(self.run_subsuite.__func__, args)
        dead = False

        while True:
            if result.shouldStop:
                pool.terminate()
                dead = True
                break

            try:
                subsuite_index, events = test_results.next(timeout=0.1)
            except multiprocessing.TimeoutError:
                continue
            except StopIteration:
                break

            tests = list(self.subsuites[subsuite_index])
            for event in events:
                event_name = event[0]
                handler = getattr(result, event_name, None)
                if handler is None:
                    continue
                test = tests[event[1]]
                args = event[2:]
                handler(test, *args)

        if not dead:
            args = [tuple() for _i in range(self.processes)]
            results = pool.imap_unordered(save_coverage, args)
            for result in results:
                # Exhaust the generator, ensuring each process ran its part.
                pass
            pool.close()
        # Super uses pool.join, but this has failed ever since UserMatchesMixin got ddt and data added to it.
        # unclear why, but .terminate doesn't seem to have any bad consequences for our use case, so we use that
        # instead.
        pool.terminate()

        return result


class NPMBuildTestRunner(DiscoverRunner):
    parallel_test_suite = CoveredParallelTestSuite

    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)
        self.run_build = kwargs.pop('run_build')
        self.e2e = kwargs.pop('e2e')
        self.coverage = kwargs.pop('coverage')
        self.time_detailed = kwargs.pop('time_detailed')
        self.time = kwargs.pop('time')
        if self.time_detailed:
            self.time = self.time_detailed
        if not self.e2e:
            self.exclude_tags.add('e2e')
        self.max_time = kwargs.pop('max_time')
        if kwargs.pop('rebuild_fixtures'):
            os.environ['REBUILD_FIXTURES'] = '1'
        self.time_reports = Queue()
        self.class_time_reports = Queue()
        self.time_reports.cancel_join_thread()
        self.class_time_reports.cancel_join_thread()
        self.coverage_reporter = None

    def instrument_time_checks(self):
        from unittest import TestCase
        class_time_reports = self.class_time_reports
        time_reports = self.time_reports

        # noinspection PyDecorator,PyPep8Naming
        @classmethod
        def setUpClass(cls):
            cls.class_start_time = time.time()

        # noinspection PyDecorator,PyPep8Naming
        @classmethod
        def tearDownClass(cls):
            class_time_reports.put((f'{cls.__module__}.{cls.__name__}', time.time() - cls.class_start_time))

        TestCase.setUpClass = setUpClass
        TestCase.tearDownClass = tearDownClass
        if not self.time_detailed:
            return

        # noinspection PyPep8Naming,PyShadowingNames
        def setUp(self):
            self.method_start_time = time.time()

        # noinspection PyPep8Naming,PyShadowingNames
        def tearDown(self):
            execution_time = time.time() - self.method_start_time
            time_reports.put(
                (f'{self.__class__.__module__}.{self.__class__.__name__}.{self._testMethodName}', execution_time)
            )

        TestCase.setUp = setUp
        TestCase.tearDown = tearDown

    def setup_test_environment(self, **kwargs):
        super().setup_test_environment(**kwargs)
        if self.run_build:
            call(['cp', 'webpack-stats.json', 'webpack-stats-bak.json'])
            call(['npm', 'run', 'build'])
            call(['cp', 'webpack-stats.json', 'webpack-stats-saved.json'])
            call(['cp', 'webpack-stats-bak.json', 'webpack-stats.json'])
            call(['./manage.py', 'collectstatic', '--noinput', '-v0'])
        settings.WEBPACK_LOADER['DEFAULT']['STATS_FILE'] = os.path.join(
            settings.BASE_DIR, 'webpack-stats-saved.json'
        )
        if self.time:
            self.instrument_time_checks()

    def run_time_report(self):
        def queue_yield():
            while not self.time_reports.empty():
                yield self.time_reports.get()
        reports = [report for report in queue_yield()]
        reports.sort(key=lambda report: report[1], reverse=True)
        for report in reports:
            name, execution_time = report
            if execution_time < (.25 * self.max_time):
                color = "\033[92m"
            elif execution_time < self.max_time:
                color = "\033[93m"
            else:
                color = "\033[91m"
            print("%s%s: %.3f seconds\033[0m" % (color, name, execution_time))

    def suite_result(self, suite, result, **kwargs):
        code = super().suite_result(suite, result, **kwargs)
        self.run_time_report()
        if not self.coverage:
            return code
        coverage.process_startup.coverage.stop()
        coverage.process_startup.coverage.save()
        # Prevents writing of additional coverage file on process exit.
        # This is not a public interface, so be warned-- it might break some day.
        coverage.process_startup.coverage._auto_save = False
        call(['coverage', 'combine'])
        call(['coverage', 'html'])
        return code + call(['coverage', 'report'])

    @classmethod
    def add_arguments(cls, parser):
        super().add_arguments(parser)
        parser.add_argument(
            '--run-build', action='store_true', dest='run_build',
            help='Build and collect static assets.',
        )
        parser.add_argument(
            '--e2e', action='store_true', dest='e2e',
            help='Run the end-to-end tests.',
        )
        parser.add_argument(
            '--coverage', action='store_true', dest='coverage',
            help='Collects and displays coverage report on the results.',
        )
        parser.add_argument(
            '--time', action='store_true', dest='time',
            help='Annotates test cases with timing information.'
        )
        parser.add_argument(
            '--time-detailed', action='store_true', dest='time_detailed',
            help='Annotates individual tests with timing information. Implies --time.'
        )
        parser.add_argument(
            '--max-time', type=float, dest='max_time',
            help='Tests that take longer than this many seconds are marked red. Default: 3.5',
            default=3.5,
        )
        parser.add_argument(
            '--rebuild-fixtures', action='store_true', dest='rebuild_fixtures',
        )


class DisableCSRF:
    def __init__(self, get_response):
        self.get_response = get_response

    def __call__(self, request):
        setattr(request, '_dont_enforce_csrf_checks', True)
        return self.get_response(request)


def create_fixture(filename):
    buf = StringIO()
    management.call_command('dumpdata', stdout=buf)
    buf.seek(0)
    with open(filename, 'w') as f:
        f.write(buf.read())


class SimpleAuthRequestFactory(APIRequestFactory):
    def request(self, **request):
        req = super().request(**request)
        req.authenticators = False
        return req


@ddt
class PermissionsTestCase(APITestCase):
    view_class = GenericAPIView
    args = []
    kwargs = {}

    def setUp(self):
        super().setUp()
        self.factory = SimpleAuthRequestFactory()
        self.user = Mock(spec=User)
        self.user2 = Mock(spec=User)
        self.staff = Mock(spec=User)
        self.anonymous = Mock(spec=AnonymousUser)
        self.user.label = 'user'
        self.user.is_staff = False
        self.user.is_superuser = False
        self.user.is_authenticated = True
        self.user2.label = 'outsider'
        self.user2.is_staff = False
        self.user2.is_superuser = False
        self.user2.is_authenticated = True
        self.staff.label = 'staff'
        self.staff.is_staff = True
        self.staff.is_superuser = False
        self.staff.is_authenticated = True
        self.anonymous.label = 'anonymous'
        self.anonymous.is_staff = False
        self.anonymous.is_authenticated = False
        self.anonymous.is_superuser = False
        self.view = self.view_class()

    def check_perms(self, request, *args, fails=True, **kwargs):
        try:
            if not hasattr(self.view_class, request.method.lower()):
                raise PermissionDenied(f'Method {request.method} not allowed on {self.view_class}.')
            self.view.check_object_permissions(request, *args, **kwargs)
        except PermissionDenied:
            if fails:
                return
            raise
        if fails:
            raise AssertionError('Permission check passed when it should not have!')

    def mod_request(self, request):
        request.subject = self.user

    # noinspection PyMethodMayBeStatic
    def get_object(self):
        """
        Override this if you need to change what object is returned by get_object on the target when doing the
        permissions run check.
        :return:
        """
        return Mock()

    @data('get', 'post', 'patch', 'delete', 'put')
    def test_ran_permissions_check(self, method):
        """
        Verify that the view calls check_object_permissions. The catch with this is that
        each view verified by this test will need to run the permissions check in the relevant method.
        """
        if not hasattr(self.view, method):
            # No implementation for this method.
            return
        patcher = patch.object(self.view, 'check_object_permissions')
        check_object_perms = patcher.start()
        patch.object(self.view, 'get_object').start()
        patch.object(self.view, 'get_queryset').start()
        request = getattr(self.factory, method)('/', *self.args, **self.kwargs)
        self.mod_request(request)
        self.view.request = request
        self.view.args = self.args
        self.view.kwargs = self.kwargs
        # noinspection PyBroadException
        try:
            getattr(self.view, method)(request, *self.args, **self.kwargs)
        except Exception as err:
            if not check_object_perms.called:
                raise AssertionError(f'Ran into exception before permissions check was called: {err}')
        self.assertTrue(check_object_perms.called)


# noinspection PyUnresolvedReferences
@ddt
class MethodAccessMixin:
    # Everyone fails by default. You must explicitly define who passes by setting the user's username
    # in the relevant list.
    passes = {'get': [], 'post': [], 'patch': [], 'delete': [], 'put': []}

    @data('get', 'post', 'patch', 'delete', 'put')
    def test_outsider(self, method):
        request = getattr(self.factory, method)('/')
        request.user = self.user2
        self.mod_request(request)
        fails = self.user2.label not in self.passes[method]
        self.check_perms(request, self.user, fails=fails)

    @data('get', 'post', 'patch', 'delete', 'put')
    def test_not_logged_in(self, method):
        request = getattr(self.factory, method)('/')
        request.user = self.anonymous
        self.mod_request(request)
        fails = self.anonymous.label not in self.passes[method]
        self.check_perms(request, self.user, fails=fails)

    @data('get', 'post', 'patch', 'delete', 'put')
    def test_staff(self, method):
        request = getattr(self.factory, method)('/')
        request.user = self.staff
        self.mod_request(request)
        fails = self.staff.label not in self.passes[method]
        self.check_perms(request, self.user, fails=fails)

    @data('get', 'post', 'patch', 'delete', 'put')
    def test_self(self, method):
        request = getattr(self.factory, method)('/')
        request.user = self.user
        self.mod_request(request)
        fails = self.user.label not in self.passes[method]
        self.check_perms(request, self.user, fails=fails)

    def get_object(self):
        return self.user


class SignalsDisabledMixin:
    def setUp(self):
        super().setUp()
        self.disabler = signal_disabler.disable()
        self.disabler.disconnect_all()

    def tearDown(self):
        super().tearDown()
        self.disabler.reconnect_all()
