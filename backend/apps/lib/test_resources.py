import inspect
import json
import os
from pprint import pformat
from subprocess import call

from bok_choy.browser import BROWSERS
from bok_choy.page_object import PageObject, unguarded
from bok_choy.promise import EmptyPromise, BrokenPromise, Promise
from bok_choy.web_app_test import WebAppTest
from django.conf import settings
from django.forms import CheckboxInput, RadioSelect
from django.test import LiveServerTestCase, TestCase
from django.test.runner import DiscoverRunner
from django.urls import reverse
from needle.driver import NeedleFirefox
from pyvirtualdisplay import Display
from rest_framework.test import APIClient
from seleniumrequests import RequestMixin

from apps.profiles.tests.factories import UserFactory


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
        os.environ['SCREENSHOT_DIR'] = os.path.join(settings.BASE_DIR, 'tests', 'logs')
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
        self.wait_for(lambda: not self.q_toggle(css=element_selector, root=root).present, description=description, timeout=timeout)

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


class memoized_property(property):
    pass


class CheckBox(object):
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


class APITestCase(TestCase):
    def setUp(self):
        super().setUp()
        self.client = APIClient()
        self.user = UserFactory.create()
        self.user2 = UserFactory.create()
        self.staffer = UserFactory.create(username='staffer', is_staff=True, email='staff@example.com')

    def login(self, user):
        result = self.client.login(email=user.email, password='Test')
        self.assertIs(result, True)

    @staticmethod
    def assertIDInList(member, container):
        for item in container:
            if item['id'] == member.id:
                break
        else:
            raise AssertionError("ID {} not found in: {}".format(
                member.id,
                '[' + ',\n'.join([pformat(item) for item in container]) + ']')
            )


class NPMBuildTestRunner(DiscoverRunner):
    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)
        self.run_build = kwargs.pop('run_build')

    def setup_test_environment(self, **kwargs):
        super().setup_test_environment(**kwargs)
        if self.run_build:
            call(['npm', 'run', 'build'])
            call(['./manage.py', 'collectstatic', '--noinput', '-v0'])

    @classmethod
    def add_arguments(cls, parser):
        super().add_arguments(parser)
        parser.add_argument(
            '--run-build', action='store_true', dest='run_build',
            help='Build and collect static assets.',
        )
