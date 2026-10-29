@echo off
echo abre el html sin cors pq sino no va
start msedge --disable-web-security --user-data-dir="%TEMP%\edge_no_cors" "api-test.html"
