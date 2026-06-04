# Channel Setup FAQ

Source ID: faq-channel-setup

## Supported Channels

SupportFlow accepts inquiries from email forwarding, web widget, REST API, and supported chat integrations. Every inbound message becomes a conversation with a channel field and source identifier.

## Email Forwarding

Configure the mailbox to forward support messages to the generated SupportFlow address. Validate SPF and DKIM before enabling customer-facing replies from the same domain.

## Web Widget

Install the widget snippet on authenticated product pages. Pass customer ID and plan only from trusted server-side context. Do not place secret tokens in the browser snippet.

## REST API

Use the Conversations API for server-created inquiries from product workflows. Include idempotency keys for retryable submissions.

## Chat Integrations

Chat integrations should be mapped to a queue and business-hours calendar. After-hours chat messages should receive an automatic acknowledgement with the next expected response window.
