import logging
import ElasticEmail
from ElasticEmail.api import emails_api
from ElasticEmail.model.email_message_data import EmailMessageData
from ElasticEmail.model.email_recipient import EmailRecipient

from .templates import templates_data


logging.basicConfig(format='%(asctime)s - %(message)s', level=logging.INFO)


def send_email(key, email_from, msg):
    configuration = ElasticEmail.Configuration()
    configuration.api_key['apikey'] = key

    try:
        with ElasticEmail.ApiClient(configuration) as api_client:
            api_instance = emails_api.EmailsApi(api_client)
            email_message_data = EmailMessageData(
                recipients=[EmailRecipient(email=i['email'], fields={k: v for k, v in i.items()}) for i in msg['data']],
                content={
                    "Body": [
                        {
                            "ContentType": "HTML",
                            "Content": templates_data[msg['template_id']]
                        }
                    ],
                    "Subject": msg['subject'],
                    "From": email_from
                }
            )

            try:
                api_response = api_instance.emails_post(email_message_data)
                logging.info(api_response)
                return api_response

            except ElasticEmail.ApiException as e:
                logging.warning("Exception when calling EmailsApi->emails_post: %s\n" % e)
            except Exception as e:
                logging.error(f'Error: {str(e)}')
    except Exception as e:
        logging.error(f'Error: {str(e)}')
