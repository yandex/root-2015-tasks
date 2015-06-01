#!/usr/bin/env bash

FLOW_DIR=/var/nflow
REPORT=/usr/share/nginx/www/billing.html

echo '<html><body>' > "$REPORT"
flow-cat "$FLOW_DIR"/ft* \
    | flow-filter -f/root/nflow/flow.acl -Sinternet -Dlocalnet \
    | flow-report -s /root/nflow/report.conf -S localnet \
    | flow-rptfmt -fhtml -H >> "$REPORT"
echo '</html></body>' >> "$REPORT"
