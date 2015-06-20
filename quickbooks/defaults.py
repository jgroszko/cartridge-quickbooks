from mezzanine.conf import register_setting

register_setting(
    name="QUICKBOOKS_CONSUMER_KEY",
    description="QuickBooks Consumer Key",
    editable=False,
)

register_setting(
    name="QUICKBOOKS_CONSUMER_SECRET",
    description="QuickBooks Consumer Secret",
    editable=False
)
