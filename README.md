# sendgrid-email modular resource

This module implements the [rdk generic API](https://github.com/rdk/generic-api) in a viam-soleng:messaging:sendgrid-email model.
With this model, you can send emails with the Sendgrid email service, including support for attachments.

## Requirements

A Sendgrid account must be set up with a verified email address, and a Sendgrid API key must be acquired.

## Build and run

To use this module, follow the instructions to [add a module from the Viam Registry](https://docs.viam.com/registry/configure/#add-a-modular-resource-from-the-viam-registry) and select the `viam-soleng:messaging:sendgrid-email` model from the [`viam-soleng:messaging:sendgrid-email` module](https://app.viam.com/module/rdk/viam-soleng:messaging:sendgrid-email).

## Configure your email service

> [!NOTE]  
> Before configuring your email service, you must [create a machine](https://docs.viam.com/manage/fleet/machines/#add-a-new-machine).

Navigate to the **Config** tab of your machine's page in [the Viam app](https://app.viam.com/).
Click on the **Components** subtab and click **Create component**.
Select the `generic` type, then select the `viam-soleng:messaging:sendgrid-email` model.
Click **Add module**, then enter a name for your generic and click **Create**.

On the new component panel, copy and paste the following attribute template into your generic’s **Attributes** box:

```json
{
  "api_key": "<your sendgrid api key>"
}
```

> [!NOTE]  
> For more information, see [Configure a Machine](https://docs.viam.com/manage/configuration/).

### Attributes

The following attributes are available for `viam-soleng:messaging:sendgrid-email` service configuration:

| Name | Type | Inclusion | Description |
| ---- | ---- | --------- | ----------- |
| `api_key` | string | **Required** |  Sendgrid API key |
| `default_from` | string | Optional |  Default Sendgrid verified email address to send from, optional as it can be passed on each send request. |
| `default_from_name` | string | Optional |  Default from name to associate with the from address, optional as it can be passed on each send request, and if not present will use default_from as the name. |
| `preset_messages` | object | Optional|  An object with key (preset name) and value (object with subject and body) pairs that can be used to send pre-configured messages. HTML is accepted in the body of each. Template strings can be embedded within double angle brackets, for example: <<to_replace>>|
| `enforce_preset` | boolean | Optional, default false |  If set to true, preset_messages must be configured and a preset message must be selected when sending. |

### Example configuration

```json
{
  "api_key": "SG.abc123-ds-er-23-da",
  "enforce_preset": true,
  "preset_messages": {
    "welcome": {
      "subject": "welcome to the service",
      "body": "<b>Great to have you!</b>"
    },
    "alert": {
      "subject": "Alert: <<about>>",
      "body": "This is an alert message about <<about>>."
    }
  }
}
```

## API

The Sendgrid email service provides the [DoCommand](https://docs.viam.com/services/generic/#docommand) method from Viam's built-in [rdk:service:generic API](https://docs.viam.com/services/generic/)

### do_command(*dictionary*)

In the dictionary passed as a parameter to do_command(), you must specify a *command* by passing a the key *command* with one of the following values.

#### send

When *send* is passed as the command, an email will be sent via the configured Sendgrid account.
The following may also be passed:

| Key | Type | Inclusion | Description |
| ---- | ---- | --------- | ----------- |
| `to` | string | **Required** |  The email to send the message to. |
| `subject` | string | **Required** |  The email subject. |
| `body` | string | Optional |  The email message text, HTML is accepted. |
| `from` | string | Optional |  The sendgrid verified email address from which to send the message. If not specified, will use *default_from*, if configured. |
| `from_name` | string | Optional |  A name to associate with the from email address. If not specified, will use *default_from_name*, if configured. |
| `preset` | string | Optional |  The name of a configured preset message, configured with preset_messages.  If the service is configured with enforce_preset=true, this becomes required. |
| `template_vars` | object | Optional | A key/value pair of template parameter names and values to insert into preset messages. |
| `attachments` | list[object] | Optional | A list of attachments, each with *content* (Base64-encoded string), *filename* (string), and *mime_type* (string). Attachments are added in the order listed. |

### Attachments

The *attachments* field allows you to include files in your email. Each attachment is an object with:
* `content`: Base64-encoded string of the file content.
* `filename`: Name of the file, including extension (e.g., `report.xlsx`).
* `mime_type`: MIME type of the file, determining how email clients handle it.

#### Common MIME types

| File Type | Extension | MIME Type | 
| ---- | ---- | --------- |
| CSV | .csv | text/csv |
| Plain Text | .txt | text/plain | 
| JPEG Image | .jpg, .jpeg | image/jpeg |
| PNG Image | .png | image/png |
| Word Document | .docx | application/vnd.openxmlformats-officedocument.wordprocessingml.document |
| Excel | .xlsx | application/vnd.openxmlformats-officedocument.spreadsheetml.sheet |
| PDF | .pdf | application/pdf |

For other MIME types, refer to the [IANA MIME Type Registry](https://www.iana.org/assignments/media-types/media-types.xhtml). If unspecified, mime_type defaults to application/octet-stream, which may prompt a download without preview.

#### Notes
* Ensure Base64-encoded attachment content is valid to avoid SendGrid API errors.
* SendGrid imposes a 30MB limit on email size, including attachments. Compress large files (e.g., using ZIP) if needed.
* Test attachment rendering in email clients (e.g., Gmail, Outlook) to confirm MIME type compatibility.