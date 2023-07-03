import ctypes
import multiprocessing
import os
import platform
import time
from decimal import Decimal
from multiprocessing import Queue
from pprint import pformat
from subprocess import call
from tempfile import TemporaryDirectory
from unittest.mock import Mock, patch

import coverage
import signal_disabler
from apps.sales.models import ServicePlan
from ddt import data, ddt
from django.conf import settings
from django.db import connections
from django.test.runner import DiscoverRunner, ParallelTestSuite
from moneyed import Money
from rest_framework.exceptions import PermissionDenied
from rest_framework.generics import GenericAPIView
from rest_framework.test import APIRequestFactory
from rest_framework.test import APITestCase as BaseAPITestCase

MIDDLEWARE = ["apps.lib.test_resources.DisableCSRF"] + settings.MIDDLEWARE


# noinspection PyPep8Naming
class memoized_property(property):
    pass


class EnsurePlansMixin:
    def setUp(self):
        super().setUp()
        self.landscape = ServicePlan.objects.get_or_create(
            name="Landscape",
            sort_value=1,
            monthly_charge=Money("8.00", "USD"),
            tipping=True,
            shield_static_price=Money(".50", "USD"),
            shield_percentage_price=Decimal("4"),
        )[0]
        self.free = ServicePlan.objects.get_or_create(
            name="Free",
            sort_value=0,
            shield_static_price=Money(".75", "USD"),
            shield_percentage_price=Decimal("8"),
            max_simultaneous_orders=1,
        )[0]


class APITestCase(EnsurePlansMixin, BaseAPITestCase):
    def login(self, user):
        result = self.client.login(email=user.email, password="Test")
        self.assertIs(result, True)

    def create_session(self):
        """
        Hacky method to force the creation of a session.
        """
        result = self.client.login(email="DoesNotExist@example.com", password="Test")
        self.assertIs(result, False)

    @staticmethod
    def assertIDInList(member, container):
        if not isinstance(member, int):
            member = member.id
        for item in container:
            if item["id"] == member:
                break
        else:
            raise AssertionError(
                "ID {} not found in: {}".format(
                    member,
                    "[" + ",\n".join([pformat(item) for item in container]) + "]",
                )
            )


_worker_id = 0


def _init_worker(counter):
    """
    Switch to databases dedicated to this worker.

    This helper lives at module-level because of the multiprocessing module's
    requirements.
    """
    global _worker_id
    import django

    django.setup()

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
        if platform.system().lower() == "darwin":
            settings_dict["NAME"] = f'test_{settings_dict["NAME"]}'
        connection.settings_dict.update(settings_dict)
        connection.close()
    # Remove parent process reference, which won't be valid.
    try:
        del coverage.process_startup.coverage
    except AttributeError:
        pass
    coverage.process_startup()


def save_coverage(*_args):
    cov = getattr(coverage.process_startup, "coverage", None)
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
            (self.runner_class, index, subsuite, self.failfast, self.buffer)
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
        # Super uses pool.join, but this has failed ever since UserMatchesMixin got ddt
        # and data added to it. unclear why, but .terminate doesn't seem to have any
        # bad consequences for our use case, so we use that instead.
        pool.terminate()

        return result


class NPMBuildTestRunner(DiscoverRunner):
    parallel_test_suite = CoveredParallelTestSuite

    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)
        self.run_build = kwargs.pop("run_build")
        self.e2e = kwargs.pop("e2e")
        self.coverage = kwargs.pop("coverage")
        self.time_detailed = kwargs.pop("time_detailed")
        self.time = kwargs.pop("time")
        if self.time_detailed:
            self.time = self.time_detailed
        if not self.e2e:
            self.exclude_tags.add("e2e")
        self.max_time = kwargs.pop("max_time")
        self.time_reports = Queue()
        self.class_time_reports = Queue()
        self.time_reports.cancel_join_thread()
        self.class_time_reports.cancel_join_thread()
        self.coverage_reporter = None
        self.media_root = TemporaryDirectory()

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
            class_time_reports.put(
                (f"{cls.__module__}.{cls.__name__}", time.time() - cls.class_start_time)
            )

        TestCase.setUpClass = setUpClass
        TestCase.tearDownClass = tearDownClass
        if not self.time_detailed:
            return

        # noinspection PyPep8Naming,PyShadowingNames
        def setUp(self):
            self.method_start_time = time.time()
            super().setUp()

        # noinspection PyPep8Naming,PyShadowingNames
        def tearDown(self):
            execution_time = time.time() - self.method_start_time
            time_reports.put(
                (
                    f"{self.__class__.__module__}.{self.__class__.__name__}."
                    f"{self._testMethodName}",
                    execution_time,
                )
            )
            super().tearDown()

        TestCase.setUp = setUp
        TestCase.tearDown = tearDown

    def setup_test_environment(self, **kwargs):
        super().setup_test_environment(**kwargs)
        if self.run_build:
            call(["cp", "webpack-stats.json", "webpack-stats-bak.json"])
            call(["npm", "run", "build"])
            call(["cp", "webpack-stats.json", "webpack-stats-saved.json"])
            call(["cp", "webpack-stats-bak.json", "webpack-stats.json"])
            call(["./manage.py", "collectstatic", "--noinput", "-v0"])
        settings.WEBPACK_LOADER["DEFAULT"]["STATS_FILE"] = os.path.join(
            settings.BASE_DIR, "webpack-stats.json"
        )
        settings.MEDIA_ROOT = self.media_root.name
        if self.time:
            self.instrument_time_checks()

    def teardown_test_environment(self, **kwargs: dict) -> None:
        self.media_root.cleanup()

    def run_time_report(self):
        def queue_yield():
            while not self.time_reports.empty():
                yield self.time_reports.get()

        reports = [report for report in queue_yield()]
        reports.sort(key=lambda report: report[1], reverse=True)
        for report in reports:
            name, execution_time = report
            if execution_time < (0.25 * self.max_time):
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
        call(["python", "-m", "coverage", "combine"])
        call(["python", "-m", "coverage", "html"])
        return code + call(["python", "-m", "coverage", "report"])

    @classmethod
    def add_arguments(cls, parser):
        super().add_arguments(parser)
        parser.add_argument(
            "--run-build",
            action="store_true",
            dest="run_build",
            help="Build and collect static assets.",
        )
        parser.add_argument(
            "--e2e",
            action="store_true",
            dest="e2e",
            help="Run the end-to-end tests.",
        )
        parser.add_argument(
            "--coverage",
            action="store_true",
            dest="coverage",
            help="Collects and displays coverage report on the results.",
        )
        parser.add_argument(
            "--time",
            action="store_true",
            dest="time",
            help="Annotates test cases with timing information.",
        )
        parser.add_argument(
            "--time-detailed",
            action="store_true",
            dest="time_detailed",
            help="Annotates individual tests with timing information. Implies --time.",
        )
        parser.add_argument(
            "--max-time",
            type=float,
            dest="max_time",
            help="Tests that take longer than this many seconds are marked red. "
            "Default: 3.5",
            default=3.5,
        )


class DisableCSRF:
    def __init__(self, get_response):
        self.get_response = get_response

    def __call__(self, request):
        setattr(request, "_dont_enforce_csrf_checks", True)
        return self.get_response(request)


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
        from apps.profiles.models import User
        from django.contrib.auth.models import AnonymousUser

        super().setUp()
        self.factory = SimpleAuthRequestFactory()
        self.user = Mock(spec=User)
        self.user2 = Mock(spec=User)
        self.staff = Mock(spec=User)
        self.anonymous = Mock(spec=AnonymousUser)
        self.user.label = "user"
        self.user.is_staff = False
        self.user.is_superuser = False
        self.user.is_authenticated = True
        self.user2.label = "outsider"
        self.user2.is_staff = False
        self.user2.is_superuser = False
        self.user2.is_authenticated = True
        self.staff.label = "staff"
        self.staff.is_staff = True
        self.staff.is_superuser = False
        self.staff.is_authenticated = True
        self.anonymous.label = "anonymous"
        self.anonymous.is_staff = False
        self.anonymous.is_authenticated = False
        self.anonymous.is_superuser = False
        self.view = self.view_class()

    def check_perms(self, request, *args, fails=True, **kwargs):
        try:
            if not hasattr(self.view_class, request.method.lower()):
                raise PermissionDenied(
                    f"Method {request.method} not allowed on {self.view_class}."
                )
            self.view.check_permissions(request)
            self.view.check_object_permissions(request, *args, **kwargs)
        except PermissionDenied:
            if fails:
                return
            raise
        if fails:
            raise AssertionError(
                f"Permission check passed when it should not have! {request.method} - "
                f"{self.user.label}",
            )

    def mod_request(self, request):
        request.subject = self.user

    # noinspection PyMethodMayBeStatic
    def get_object(self):
        """
        Override this if you need to change what object is returned by get_object on the
        target when doing the permissions run check.
        :return:
        """
        return Mock()

    @data("get", "post", "patch", "delete", "put")
    def test_ran_permissions_check(self, method):
        """
        Verify that the view calls check_object_permissions. The catch with this is that
        each view verified by this test will need to run the permissions check in the
        relevant method.
        """
        if not hasattr(self.view, method):
            # No implementation for this method.
            return
        patcher = patch.object(self.view, "check_object_permissions")
        check_object_perms = patcher.start()
        patch.object(self.view, "get_object").start()
        patch.object(self.view, "get_queryset").start()
        request = getattr(self.factory, method)("/", *self.args, **self.kwargs)
        self.mod_request(request)
        self.view.request = request
        self.view.args = self.args
        self.view.kwargs = self.kwargs
        # noinspection PyBroadException
        try:
            getattr(self.view, method)(request, *self.args, **self.kwargs)
        except Exception as err:
            if not check_object_perms.called:
                raise AssertionError(
                    f"Ran into exception before permissions check was called: {err}"
                )
        self.assertTrue(check_object_perms.called)


# noinspection PyUnresolvedReferences
@ddt
class MethodAccessMixin:
    # Everyone fails by default. You must explicitly define who passes by setting the
    # user's username in the relevant list.
    passes = {"get": [], "post": [], "patch": [], "delete": [], "put": []}

    @data("get", "post", "patch", "delete", "put")
    def test_outsider(self, method):
        request = getattr(self.factory, method)("/")
        request.user = self.user2
        self.mod_request(request)
        fails = self.user2.label not in self.passes[method]
        self.check_perms(request, self.user, fails=fails)

    @data("get", "post", "patch", "delete", "put")
    def test_not_logged_in(self, method):
        request = getattr(self.factory, method)("/")
        request.user = self.anonymous
        self.mod_request(request)
        fails = self.anonymous.label not in self.passes[method]
        self.check_perms(request, self.user, fails=fails)

    @data("get", "post", "patch", "delete", "put")
    def test_staff(self, method):
        request = getattr(self.factory, method)("/")
        request.user = self.staff
        self.mod_request(request)
        fails = self.staff.label not in self.passes[method]
        self.check_perms(request, self.user, fails=fails)

    @data("get", "post", "patch", "delete", "put")
    def test_self(self, method):
        request = getattr(self.factory, method)("/")
        request.user = self.user
        self.mod_request(request)
        fails = self.user.label not in self.passes[method]
        self.check_perms(request, self.user, fails=fails)

    def get_object(self):
        return self.user


disable = signal_disabler.disable()


class SignalsDisabledMixin:
    def setUp(self):
        super().setUp()
        self.disabler = disable
        self.disabler.disconnect_all()

    def tearDown(self):
        super().tearDown()
        signals = self.disabler.stashed_signals.keys()
        self.disabler.reconnect_all()
        for signal in signals:
            signal.sender_receivers_cache.clear()
