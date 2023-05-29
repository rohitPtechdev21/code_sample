from django.utils import timezone
from django.utils.text import slugify
from django.conf import settings as s
from ckeditor.fields import RichTextField
from django.db import models


class Subscription(CommonSubscription):
    objects = models.Manager()

    # Main subscription title is also used to query this subscription and should not be changed
    title = models.CharField(
        "Title",
        max_length=255,
        help_text="This main subscription title is used to find the subscription and should not be changed."
        )


    slug = models.SlugField(
        unique=True, db_index=True, null=True, blank=False, editable=False
    )
    tagline = models.CharField("Tagline", max_length=255, blank=True, null=True)
    image = models.FileField(upload_to ='uploads/')
    complexity = models.CharField(
        "Complexity", max_length=255, blank=True, null=True
    )
    duration = models.CharField(
        "Duration", max_length=255, blank=True, null=True
    )
    marketing_goals = models.ManyToManyField(
        "tags.MarketingGoal", related_name="subscription", blank=True,
    )
    # List of tags to add to the subscription
    skills = models.ManyToManyField(
        "tags.Skill", related_name="subscription", blank=True,
    )
    is_published = models.BooleanField(
        default=False,
        help_text="Unpublished subscriptions are only visible "
        "for Users with flag is_staff=True",
    )
    is_teaser = models.BooleanField(
        default=False,
        help_text="If True, this subscription will be displayed "
        "in a minified version",
    )
    related_title = models.TextField(
        null=True, blank=True, verbose_name="Header above subscriptions in place"
    )
    other_title = models.TextField(
        null=True, blank=True, verbose_name="Header above next subscriptions"
    )


    modified_on = models.DateTimeField(default=timezone.now)

    def _skills_set(self):
        return [x.name for x in self.skills.all()]

    def _skill_categories_set(self):
        return [category.name for category in self.skill_categories.all()]

    def _parts_set(self):
        return [
            {
                "lower_amount": x.lower_amount,
                "upper_amount": x.upper_amount,
                "order": x.order,
            }
            for x in self.parts.all()
        ]

    def part1_lower_amount(self):
        parts = self.parts.order_by("order")
        part_1 = parts.first()
        if part_1 is None:
            return None
        return part_1.lower_amount

    def parts_total_lower_amount(self):
        parts = self.parts.order_by("order")
        part_1 = parts.first()
        if part_1 is None:
            return None
        return sum([part.lower_amount for part in parts if part.lower_amount])

    def check_is_published_and_not_teaser(self):
        return self.is_published and not self.is_teaser

    def image_url(self):
        if not self.image:
            return
        return self.image.url

    def subscription_pretty_url(self):
        if not self.slug:
            return
        return s.subscription.format(self.slug)

    def save(self, *args, **kwargs):
        if not self.title.strip():
            raise ValueError("Title can't be empty")

        self.slug = slugify(self.title)
        self.modified_on = timezone.now()

        super(Subscription, self).save(*args, **kwargs)

    def __str__(self):
        return f"Subscription - {self.title}"


class Common(UUIDModel):
    heading = models.CharField(max_length=100)
    order = models.PositiveSmallIntegerField()
    title = models.CharField("Public Title", max_length=255)
    title_tooltip = models.CharField("Public Title Tooltip", max_length=255)
    content = RichTextField()
    active = models.BooleanField(default=True)
    upload = models.FileField(upload_to ='uploads/')


    class Meta:
        abstract = True
