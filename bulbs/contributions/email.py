"""Module to generate and send a report to contributors containing a log of their contributions."""
from django.conf import settings
from django.contrib.auth import get_user_model
from django.core.mail import EmailMultiAlternatives
from django.template import loader
from django.utils import timezone


User = get_user_model()


# Define constants.
CONTRIBUTION_SETTINGS = getattr(settings, "CONTRIBUTIONS", {})
EMAIL_SETTINGS = CONTRIBUTION_SETTINGS.get("EMAIL", {})
DEFAULT_SUBJECT = "Contribution Report."
TEMPLATE = "reporting/__contribution_report.html"


class ContributorReport(object):
    """Generate a contributor email report."""

    def __init__(self, contributor, **kwargs):
        self.contributor = contributor

        self.now = timezone.now()
        self.month = kwargs.get("month", self.now.month)
        self.year = kwargs.get("year", self.now.year)

        self._contributions = None
        self._deadline = kwargs.get("deadline")
        self._start = kwargs.get("start")
        self._end = kwargs.get("end")

        self._total = 0

    def send(self):
        if self.is_valid():
            mail = EmailMultiAlternatives(
                subject=EMAIL_SETTINGS.get("SUBJECT", DEFAULT_SUBJECT),
                from_email=EMAIL_SETTINGS.get("FROM"),
                bcc=EMAIL_SETTINGS.get("BCC"),
                headers={"Reply-To": EMAIL_SETTINGS.get("REPLY_TO")}
            )
            mail.attach_alternative(self.get_body(), "text/html")
            if EMAIL_SETTINGS.get("ACTIVE", False):
                mail.to = [self.contributor.email]
            else:
                mail.to = EMAIL_SETTINGS.get("TO")
            mail.send()

    def get_body(self):
        contribution_types = {}
        for contribution in self.contributions:
            contribution_types[contribution] = contribution.content._meta.concrete_model.__name__
        context = {
            "content_type": contribution.content._meta.concrete_model.__name__,
            "contributor": self.contributor,
            "contributions": contribution_types,
            "deadline": self.deadline,
            "total": self.total
        }
        return loader.render_to_string(TEMPLATE, context)

    def is_valid(self):
        """returns `True` if the report should be sent."""
        if not self.total:
            return False
        if not self.contributor.freelanceprofile.is_freelance:
            return False
        return True

    @property
    def contributions(self):
        if self._contributions is None:
            self._contributions = self.contributor.contributions.filter(
                content__published__gte=self.start,
                content__published__lt=self.end
            )
        return self._contributions

    @property
    def total(self):
        if self._total == 0 and self.contributions:
            self._total = sum(
                [contribution.pay for contribution in self.contributions if contribution.pay]
            )
        return self._total

    @property
    def deadline(self):
        """Return next day as deadline if no deadline provided."""
        if not self._deadline:
            self._deadline = self.now + timezone.timedelta(days=1)
        return self._deadline

    @property
    def start(self):
        if not self._start:
            self._start = timezone.datetime(day=1, month=self.month, year=self.year)
        return self._start

    @property
    def end(self):
        if not self._end:
            next_month = (self.start.month + 1) % 12
            year = self.start.year
            if next_month == 1:
                year += 1
            elif next_month == 0:
                next_month = 12
            self._end = timezone.datetime(day=1, month=next_month, year=year)
        return self._end


class EmailReport(object):
    """Generate an email report for contributors."""

    def __init__(self, **kwargs):
        # if "start" in kwargs:
        self.now = timezone.now()
        self.month = kwargs.get("month", self.now.month)
        self.year = kwargs.get("year", self.now.year)

        self._contributors = []
        self._deadline = kwargs.get("deadline")
        self._start = kwargs.get("start")
        self._end = kwargs.get("end")

    def send_contributor_email(self, contributor):
        """Send an EmailMessage object for a given contributor."""
        ContributorReport(
            contributor,
            month=self.month,
            year=self.year,
            deadline=self._deadline,
            start=self._start,
            end=self._end
        ).send()

    def send_mass_contributor_emails(self):
        """Send report email to all relevant contributors."""
        # If the report configuration is not active we only send to the debugging user.
        if EMAIL_SETTINGS.get("ACTIVE", False):
            for contributor in self.contributors:
                if contributor.email not in EMAIL_SETTINGS.get("EXCLUDED", []):
                    self.send_contributor_email(contributor)
        else:
            for email in EMAIL_SETTINGS.get("TO", []):
                self.send_contributor_email(User.objects.get(email=email))

    def get_contributors(self):
        """Return a list of contributors with contributions between the start/end dates."""
        return User.objects.filter(
            contributions__content__published__gte=self.start,
            contributions__content__published__lt=self.end
        ).distinct()

    @property
    def contributors(self):
        """Property to retrieve or access the list of contributors."""
        if not self._contributors:
            self._contributors = self.get_contributors()
        return self._contributors

    @property
    def start(self):
        if not self._start:
            self._start = timezone.datetime(day=1, month=self.month, year=self.year)
        return self._start

    @property
    def end(self):
        if not self._end:
            next_month = (self.start.month + 1) % 12
            year = self.start.year
            if next_month == 1:
                year += 1
            elif next_month == 0:
                next_month = 12
            self._end = timezone.datetime(day=1, month=next_month, year=year)
        return self._end
