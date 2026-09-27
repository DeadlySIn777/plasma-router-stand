"""Pure byte decoder and MCP23017 initialization contract; no bus access."""
import json
from pathlib import Path

PLAN=json.loads(Path(__file__).with_name('io_plan.json').read_text(encoding='utf-8'))

# BANK=0, sequential mode. Read configuration back after every reset and at least
# every100ms; any mismatch invalidates snapshot. GPINTEN zero: no new MCU EXTI.
INIT_WRITES=((0x14,0x00),(0x15,0x00),(0x0A,0x00),(0x00,0x7F),(0x01,0x7F),
             (0x02,0x00),(0x03,0x00),(0x04,0x00),(0x05,0x00),(0x0C,0x00),(0x0D,0x00))


def decode_gpio(a,b):
    if not (isinstance(a,int) and isinstance(b,int) and 0<=a<=255 and 0<=b<=255):
        raise ValueError('Require a completed two-byte unsigned snapshot')
    return {item['signal']:not bool((a if item['mcp'][2]=='A' else b) & (1<<int(item['mcp'][3])))
            for item in PLAN['isolated_inputs']}


def config_valid(registers):
    return all(registers.get(reg)==value for reg,value in INIT_WRITES)
