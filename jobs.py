import html
import requests
import json
from django_rq import job
from datetime import date
from api2pdf import Api2Pdf

from django.conf import settings
from django.core.files.base import ContentFile
from django.template import Context, Template


@job
def common_user_contract_pdfs(contract):
    from .models import (
        SubscriptionTemplatePDF,
        ContractPDF,
    )

    today = date.today()

    a2p_client = Api2Pdf(settings.API2PDF)

    for sp_template_pdf in SubscriptionTemplatePDF.objects.filter(
        subscription=contract.subscription
    ):
        contract_pdf = ContractPDF.objects.create(
            contract=contract, is_client=sp_template_pdf.is_client,
        )

        if settings.API2PDF:
            try:
                amounts = contract.get_contract_payment_amounts()

                template = Template(html.unescape(sp_template_pdf.content))
                context = Context(
                    {
                        "today": today,
                        "client": contract.client,
                        "user": contract.user,
                        "contract": contract,
                        "amounts": amounts,
                    }
                )

                generated = template.render(context)

                api_response = a2p_client.WkHtmlToPdf.convert_from_html(
                    generated
                )

                path = f"subscriptions-contracts/{contract_pdf.uuid}.pdf"
                contract_pdf.file.storage.save(
                    path, ContentFile(api_response.download_pdf())
                )

                contract_pdf.file = path
                contract_pdf.response = api_response.result
            except Exception as err:
                contract_pdf.error = str(err)

            contract_pdf.save()


@job
def slack_webhook_new_user_subscriptions_message(**kwargs):
    if not settings.SLACK_WEBHOOK_PACKAGES:
        return
    webhook_url = settings.SLACK_WEBHOOK_PACKAGES

    slack_data = kwargs.get('slack_data')

    requests.post(
        webhook_url, data=json.dumps(slack_data),
        headers={'Content-Type': 'application/json'}
    )
