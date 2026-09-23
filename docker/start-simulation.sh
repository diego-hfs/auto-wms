#!/usr/bin/env bash
set -euo pipefail

export DISPLAY="${DISPLAY:-:99}"
export XAUTHORITY="${XAUTHORITY:-/tmp/.Xauthority}"
touch "${XAUTHORITY}"
chmod 600 "${XAUTHORITY}"

FLOW="${SIMULATION_FLOW:-cadastro}"
START_DELAY="${START_DELAY:-20}"
NOVNC_URL="${NOVNC_URL:-http://localhost:6080/vnc.html?autoconnect=1&resize=scale}"

case "$FLOW" in
  cadastro) PAGE="cadastro.html" ;;
  alteracao) PAGE="alteracao.html" ;;
  *) echo "SIMULATION_FLOW inválido: $FLOW"; exit 1 ;;
esac

cleanup() {
  echo
  echo "Encerrando ambiente de simulação..."
  for pid_var in CHROMIUM_PID HTTP_PID NOVNC_PID X11VNC_PID FLUXBOX_PID XVFB_PID; do
    pid="${!pid_var:-}"
    if [[ -n "${pid}" ]]; then
      kill "${pid}" 2>/dev/null || true
    fi
  done
}
trap cleanup EXIT INT TERM

echo "Iniciando ambiente gráfico virtual em ${DISPLAY}..."
rm -f "/tmp/.X${DISPLAY#:}-lock" 2>/dev/null || true

Xvfb "${DISPLAY}" -screen 0 1280x900x24 -ac +extension RANDR >/tmp/xvfb.log 2>&1 &
XVFB_PID=$!

echo "Aguardando o Xvfb ficar disponível..."
DISPLAY_OK="false"

for tentativa in $(seq 1 30); do
  if ! kill -0 "${XVFB_PID}" 2>/dev/null; then
    echo "ERRO: Xvfb encerrou durante a inicialização."
    echo "----- /tmp/xvfb.log -----"
    cat /tmp/xvfb.log 2>/dev/null || true
    exit 1
  fi

  if xdpyinfo -display "${DISPLAY}" >/dev/null 2>&1; then
    DISPLAY_OK="true"
    echo "Xvfb disponível após ${tentativa}s."
    break
  fi

  sleep 1
done

if [[ "${DISPLAY_OK}" != "true" ]]; then
  echo "ERRO: Xvfb não respondeu após 30 segundos."
  echo "----- /tmp/xvfb.log -----"
  cat /tmp/xvfb.log 2>/dev/null || true
  exit 1
fi

fluxbox >/tmp/fluxbox.log 2>&1 &
FLUXBOX_PID=$!
sleep 1

x11vnc -display "${DISPLAY}" -forever -shared -nopw -rfbport 5900 -localhost >/tmp/x11vnc.log 2>&1 &
X11VNC_PID=$!
sleep 2

if ! kill -0 "${X11VNC_PID}" 2>/dev/null; then
  echo "ERRO: x11vnc não iniciou."
  cat /tmp/x11vnc.log 2>/dev/null || true
  exit 1
fi

start_novnc() {
  websockify --web=/usr/share/novnc 0.0.0.0:6080 localhost:5900 >/tmp/novnc.log 2>&1 &
  NOVNC_PID=$!
}

start_novnc
sleep 2

if ! kill -0 "${NOVNC_PID}" 2>/dev/null; then
  echo "ERRO: noVNC/websockify não iniciou."
  cat /tmp/novnc.log 2>/dev/null || true
  exit 1
fi

python -m http.server 8000 --directory /app/mock_wms >/tmp/mock-http.log 2>&1 &
HTTP_PID=$!
sleep 1

chromium --no-sandbox --disable-dev-shm-usage --disable-gpu --no-first-run --no-default-browser-check --kiosk --window-size=1280,900 "http://127.0.0.1:8000/${PAGE}" >/tmp/chromium.log 2>&1 &
CHROMIUM_PID=$!

echo
echo "============================================================"
echo "SIMULAÇÃO VISUAL PRONTA"
echo "Fluxo: ${FLOW}"
echo "Abra no navegador do Windows:"
echo "${NOVNC_URL}"
echo "A automação começará em ${START_DELAY} segundos."
echo "============================================================"
echo

sleep "${START_DELAY}"

if ! xdpyinfo -display "${DISPLAY}" >/dev/null 2>&1; then
  echo "ERRO: display ${DISPLAY} deixou de responder antes da automação."
  cat /tmp/xvfb.log 2>/dev/null || true
  exit 1
fi

python /app/simulacao_visual_wms.py

echo
echo "Simulação concluída com sucesso."
echo "A tela virtual permanecerá aberta até você usar Ctrl+C."
echo "Se o noVNC cair, o script tentará reiniciá-lo automaticamente."
echo

while true; do
  if ! kill -0 "${XVFB_PID}" 2>/dev/null; then
    echo "ERRO: o Xvfb parou inesperadamente."
    cat /tmp/xvfb.log 2>/dev/null || true
    exit 1
  fi

  if ! kill -0 "${NOVNC_PID}" 2>/dev/null; then
    echo "noVNC/websockify parou. Reiniciando..."
    start_novnc
    sleep 2
  fi

  sleep 5
done
