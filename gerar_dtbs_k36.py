import os
import fdt

"""
SCRIPT AUTOMÁTICO DE PATCH PARA PAINEL E CONTROLES K36 (R36S-V20 2025-05-18 2541)
Gera os DTBs estáveis com:
- LCD Reset: Pino 15 (GPIO3_B7, active-low)
- LCD Enable: Pino 13 (GPIO0_B5, active-high)
- Analógicos AMUX Enable: Pino 12 (GPIO2_B4)
- Analógicos Invert:
  - Esquerdo: invert-absx, invert-absy (correto)
  - Direito: padrão não invertido (Cima=Cima, Baixo=Baixo, Esquerda=Esquerda, Direita=Direita)
- Deadzone: 64
- Botões X/Y: Labels corretos
- Áudio: Headphone Jack Detect invertido para GPIO_ACTIVE_HIGH (0), corrigindo auto-falante
- DRAM/CPU: Stock seguro (sem crash de memória)
"""

def patch_dtb_k36(src_path, dst_path):
    with open(src_path, 'rb') as f:
        data = f.read()

    dt = fdt.parse_dtb(data)

    # 1. Panel reset pin <104 15 1>
    panel = dt.get_node('/dsi@ff450000/panel@0')
    panel.set_property('reset-gpios', [104, 15, 1])

    # 2. vcc18_lcd0 gpio <94 13 0>
    vcc = dt.get_node('/vcc18_lcd0')
    vcc.set_property('gpio', [94, 13, 0])

    # 3. vcc18-lcd-n pinctrl [0, 13, 0, 182]
    vcc_pin = dt.get_node('/pinctrl/vcc18-lcd/vcc18-lcd-n')
    vcc_pin.set_property('rockchip,pins', [0, 13, 0, 182])

    # 4. btn-pins pinctrl (troca pino 15 por 27 para desvincular do pull-up dos botoes)
    btns = dt.get_node('/pinctrl/btns/btn-pins')
    old_pins = list(btns.get_property('rockchip,pins'))
    new_pins = []
    for i in range(0, len(old_pins), 4):
        bank, pin, mux, cfg = old_pins[i:i+4]
        if bank == 3 and pin == 15:
            pin = 27
        new_pins.extend([bank, pin, mux, cfg])
    btns.set_property('rockchip,pins', new_pins)

    # 5. Joypad / Analogicos K36
    joy = dt.get_node('/odroidgo3-joypad')
    joy.set_property('amux-en-gpios', [195, 12, 1])
    joy.set_property('button-adc-deadzone', [64])
    
    # Garante que o analogico direito nao tenha inversoes indesejadas
    if joy.exist_property('invert-absrx'):
        joy.remove_property('invert-absrx')
    if joy.exist_property('invert-absry'):
        joy.remove_property('invert-absry')

    sw7 = joy.get_subnode('sw7')
    sw8 = joy.get_subnode('sw8')
    sw7.set_property('label', 'GPIO BTN-Y')
    sw8.set_property('label', 'GPIO BTN-X')

    # 6. Audio Headphone Jack Detect (hp-det-gpio)
    # Na placa R36S-V20 2025-05-18 2541, a chave mecanica do plug P2 e invertida.
    # Polaridade: GPIO_ACTIVE_HIGH (0) em vez de GPIO_ACTIVE_LOW (1), evitando
    # que o auto-falante fique mutado quando nenhum fone estiver plugado.
    snd = dt.get_node('/rk817-sound')
    hp_prop = list(snd.get_property('simple-audio-card,hp-det-gpio'))
    hp_prop[-1] = 0
    snd.set_property('simple-audio-card,hp-det-gpio', hp_prop)

    new_dtb = dt.to_dtb()

    # Validacao de integridade com fdt
    check_dt = fdt.parse_dtb(new_dtb)
    assert list(check_dt.get_node('/dsi@ff450000/panel@0').get_property('reset-gpios')) == [104, 15, 1]
    assert list(check_dt.get_node('/vcc18_lcd0').get_property('gpio')) == [94, 13, 0]
    cj = check_dt.get_node('/odroidgo3-joypad')
    assert list(cj.get_property('amux-en-gpios')) == [195, 12, 1]
    assert list(cj.get_property('button-adc-deadzone')) == [64]
    assert not cj.exist_property('invert-absrx')
    assert not cj.exist_property('invert-absry')
    assert list(check_dt.get_node('/rk817-sound').get_property('simple-audio-card,hp-det-gpio')) == [195, 22, 0]
    print("Validacao FDT concluida com sucesso!")

    with open(dst_path, 'wb') as f:
        f.write(new_dtb)
    print(f"DTB gerado com sucesso em: {dst_path} ({len(new_dtb)} bytes)")

if __name__ == '__main__':
    base_src = r'C:\Users\joel-\Desktop\boot\dtb\clone\G80C-MB V1.1-20250319 Panel 8\rk3326-r36s-linux.dtb'
    dst_out = r'C:\Users\joel-\Desktop\boot\PAINEL_K36_SOLUCAO_DEFINITIVA\rk3326-r36s-linux.dtb'
    if os.path.exists(base_src):
        patch_dtb_k36(base_src, dst_out)
    else:
        print("Arquivo base nao encontrado:", base_src)
