# MEMÓRIA DEFINITIVA DO PROJETO - R36S V20 2025-05-18 2541 (PAINEL K36)

> **Autor / Criador:** Joel Ramalho ([@JoelRamalhoF](https://github.com/JoelRamalhoF))  
> **Co-piloto Técnico:** Antigravity (Google DeepMind)  
> **Repositório Oficial:** [JoelRamalhoF/R36s_V20_2025_05_18](https://github.com/JoelRamalhoF/R36s_V20_2025_05_18)  
> **Sistemas 100% Testados e Validados:** Omni36OS (PortMaster) & DArkOSen (ArkOS)

---

## 1. Identificação do Hardware
- **Motherboard:** R36S Clone com inscrição gravada: `R36S-V20 2025-05-18 2541` (conhecida como revisão K36).
- **SoC:** Rockchip RK3326 (Quad-Core Cortex-A35, Mali-G31 MP2).
- **Controlador do Display:** KD35T133 (MIPI-DSI 4-lanes, 640x480 @ 30 MHz, DCS 370 bytes — compatível com perfil Painel 8).
- **Áudio Codec:** Rockchip RK817 (integrado no PMIC via I2S).
- **Armazenamento:** Leitor MicroSD dual / mmcblk0.

---

## 2. Diagnóstico Técnico de Falhas & Soluções (Changelog de Engenharia Reversa)

### 🔴 Falha 1: Travamento em LED Vermelho (U-Boot)
- **Causa:** O bootloader U-Boot dos clones lê os divisores ADC da placa e exige o arquivo `rg351v-uboot.dtb`. Se ausente ou incompatível com o hardware, o bootloader trava com o LED vermelho aceso (`dtb load fail` no `error.log`).
- **Solução:** Fornecidos na partição de boot os binários `rg351v-uboot.dtb`, `rg351mp-uboot.dtb` e `rg351p-uboot.dtb` (59.519 bytes) patcheados com os pinos de reset 15 e enable 13 do LCD.

### ⬛ Falha 2: Tela Preta após o Logo de Boot
- **Causa:** O `boot.ini` padrão continha `quiet splash` e `console=/dev/ttyFIQ0`, enviando a saída do Linux para uma porta serial não conectada e ocultando as falhas de inicialização.
- **Solução:** Configurado `console=tty1` para exibir a saída do Linux diretamente no visor LCD.

### 💥 Falha 3: Kernel Panic com `exitcode=0x0000000b` (Attempted to kill init!)
- **Causa:** Os DTBs antigos de K36 disponíveis na comunidade (ex.: ArkOS4Clone) continham overclocks agressivos de memória RAM (DRAM forçada a 924 MHz e 1040 MHz). Em sistemas operacionais com kernel Linux de 64 bits (`arm64`), essa frequência causava perda de integridade nos barramentos de memória e falha de segmentação (`SIGSEGV` / sinal 11) no processo `init` (`systemd`) aos 6.5 segundos de boot.
- **Solução:** O DTB foi reconstruído a partir da base oficial de clones de 2025 (`G80C-MB V1.1-20250319 Panel 8`), com timings de fábrica 100% seguros (máx 786 MHz, operação a 528/666 MHz), aplicando cirurgicamente apenas os pinos do hardware K36.

### 🕹️ Falha 4: Analógicos com Drift Severo, Descentralizados e Invertidos
- **Causa:** O multiplexador analógico da placa V20 é fisicamente chaveado pelo **Pino 12** (`GPIO2_B4`), enquanto os DTBs comuns utilizavam o pino 11 (`GPIO2_B3`). Além disso, a deadzone padrão estava em 384 e o analógico direito estava com flags de inversão desnecessárias (`invert-absrx`, `invert-absry`).
- **Solução:** Atualizado o nó `/odroidgo3-joypad`:
  - `amux-en-gpios = <195 12 1>` (Pino 12).
  - Deadzone ajustada para `64`.
  - Analógico Esquerdo: Invertido em X e Y (`invert-absx`, `invert-absy`).
  - Analógico Direito: Mapeamento direto padrão (Cima/Baixo/Esquerda/Direita).
  - Botões: `sw7 = GPIO BTN-Y`, `sw8 = GPIO BTN-X`.

### 🔊 Falha 5: Alto-Falante Mudo / Inversão no Conector de Fone de Ouvido P2
- **Causa:** O conector mecânico P2 (3.5mm) desta placa possui uma chave interna normalmente fechada (lógica inversa). O DTB padrão utilizava `simple-audio-card,hp-det-gpio = <195 22 1>` (`GPIO_ACTIVE_LOW`), fazendo com que o kernel Linux assumisse que havia fone plugado quando o conector estava vazio, mutando o alto-falante. Ao inserir um fone de ouvido, o alto-falante ligava!
- **Solução:** O pino de detecção de fone foi alterado para polaridade `GPIO_ACTIVE_HIGH` (`0`): `<195 22 0>`. Com isso:
  - Sem fone plugado: Alto-falante funciona potente e normal.
  - Ao plugar fone: O alto-falante muta automaticamente e o áudio é direcionado para a saída P2.

---

## 3. Mapeamento de Pinos da Motherboard (Pinout)
- **LCD Reset:** `GPIO3_B7` (Pino 15, active-low) -> `<104 15 1>`
- **LCD Enable (`vcc18_lcd0`):** `GPIO0_B5` (Pino 13, active-high) -> `<94 13 0>`
- **LCD Pinctrl (`vcc18-lcd-n`):** `[0, 13, 0, 182]`
- **AMUX Enable (Analógicos):** `GPIO2_B4` (Pino 12) -> `<195 12 1>`
- **Headphone Jack Detect (P2):** `GPIO2_C6` (Pino 22, active-high) -> `<195 22 0>`
- **Volume Físico:** ADC Canal 0 (`/rg351-keys`: Vol- = 166, Vol+ = 9)

---

## 4. Arquivos do Pacote de Boot
| Arquivo | Tamanho | Função |
| :--- | :--- | :--- |
| **`rk3326-r36s-linux.dtb`** | 92.433 bytes | DTB oficial do Kernel Linux para Omni36OS / ArkOS. |
| **`rk3326-k36-linux.dtb`** | 92.433 bytes | Cópia idêntica utilizada por outros sistemas (DArkOSen). |
| **`rg351v-uboot.dtb`** | 59.519 bytes | DTB do Bootloader U-Boot com pinos K36. |
| **`rg351mp-uboot.dtb`** | 59.519 bytes | DTB de compatibilidade U-Boot. |
| **`rg351p-uboot.dtb`** | 59.519 bytes | DTB de compatibilidade U-Boot. |
| **`boot.ini`** | 523 bytes | Arquivo de inicialização configurado com tty1. |
| **`gerar_dtbs_k36.py`** | ~3.5 KB | Script Python para reprodução automatizada dos patches. |
