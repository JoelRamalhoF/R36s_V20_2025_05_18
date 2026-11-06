# R36S Hardware Revision: V20 (2025-05-18 2541) - K36 Panel & Controls Support

> **Autor / Author:** Joel Ramalho ([@JoelRamalhoF](https://github.com/JoelRamalhoF))  
> **Co-piloto / Technical Co-pilot:** Antigravity (Google DeepMind)  
> **Sistemas Testados e Validados / Tested & Validated Systems:** Omni36OS (PortMaster) & DArkOSen (ArkOS)

---

## 🇧🇷 Português

### 1. Visão Geral
Este repositório contém a **solução definitiva de Device Tree (DTBs)** e arquivos de boot para a revisão de placa clone do console portátil R36S identificada pela gravação física:
```text
R36S-V20 2025-05-18 2541
```
Também referenciada na comunidade como **painel K36**.

Antes deste projeto, donos desta revisão enfrentavam:
- Console não ligando (apenas LED vermelho aceso).
- Tela preta após a logo de bootloader.
- Travamento fatal no kernel Linux com erro de tela preta ou pânico de memória:  
  `Kernel panic - not syncing: Attempted to kill init! exitcode=0x0000000b`.
- Analógicos totalmente descalibrados, com drift severo e eixos invertidos.

Este projeto realizou a engenharia reversa do hardware, reconstruiu os DTBs a partir de bases oficiais de 2025 com frequências de memória seguras e calibrou os controles físicos, tornando a placa **100% funcional** no **Omni36OS** e no **DArkOSen**.

---

### 2. Especificações de Hardware & Mapeamento de Pinos
- **Processador (SoC):** Rockchip RK3326 (Quad-Core ARM Cortex-A35, Mali-G31 MP2).
- **Controlador do Painel:** KD35T133 (MIPI-DSI 4-lanes, 640x480 @ 30 MHz, DCS 370 bytes — compatível com perfil Painel 8).
- **Mapeamento do Display (LCD):**
  - **Reset do LCD:** `GPIO3_B7` (Pino 15, active-low) -> `<104 15 1>`. *(Diferente dos clones genéricos G80C que usam pino 27)*.
  - **Alimentação/Ativação do LCD (`vcc18_lcd0`):** `GPIO0_B5` (Pino 13, active-high) -> `<94 13 0>`. *(Diferente dos clones genéricos que usam pino 3)*.
- **Mapeamento dos Analógicos e Controles:**
  - **Multiplexador Analógico (AMUX Enable):** `GPIO2_B4` (Pino 12) -> `<195 12 1>`. *(Diferente dos clones genéricos que apontam para o pino 11)*.
  - **Deadzone dos Analógicos:** `64`.
  - **Orientação de Eixos:**
    - Analógico Esquerdo: Invertido em X e Y (`invert-absx`, `invert-absy`).
    - Analógico Direito: Não invertido (orientação padrão Cima/Baixo/Esquerda/Direita).
  - **Mapeamento de Botões:** `sw7 = GPIO BTN-Y`, `sw8 = GPIO BTN-X`.
- **Frequências de Memória (DRAM) & CPU:**
  - **DRAM DMC:** Frequência stock segura (máx 786 MHz, operação a 528/666 MHz).
  - **CPU:** Máx 1512 MHz.

---

### 3. Diagnóstico de Falhas e Soluções (Changelog Técnico)

#### Falha 1: Travamento em LED Vermelho (U-Boot)
- **Causa:** O U-Boot dos consoles clone lê as pontes ADC da placa e solicita expressamente o arquivo `rg351v-uboot.dtb`. Se ausente ou incompatível, o bootloader trava com o LED vermelho aceso (`dtb load fail`).
- **Solução:** Fornecidos na partição de boot os binários `rg351v-uboot.dtb`, `rg351mp-uboot.dtb` e `rg351p-uboot.dtb` com os pinos de reset 15 e enable 13 patcheados.

#### Falha 2: Tela Preta após o Logo
- **Causa:** O `boot.ini` padrão continha `quiet splash` e `console=/dev/ttyFIQ0`, roteando a saída para uma porta serial invisível e ocultando logs de falhas.
- **Solução:** Configurado `console=tty1` para exibir a saída do Linux diretamente no visor LCD.

#### Falha 3: Kernel Panic com `exitcode=0x0000000b` (Attempted to kill init!)
- **Causa:** Os DTBs antigos de K36 disponíveis na comunidade (ex.: ArkOS4Clone) continham overclocks agressivos de memória RAM (DRAM forçada a 924 MHz e 1040 MHz). Em sistemas operacionais com kernel Linux de 64 bits (`arm64`), essa frequência causava perda de integridade nos barramentos de memória e falha de segmentação (`SIGSEGV` / sinal 11) no processo `init` (`systemd`) aos 6.5 segundos de boot.
- **Solução:** O DTB foi reconstruído a partir do DTB oficial de placas clone de 2025 (`G80C-MB V1.1-20250319 Panel 8`), com timings de fábrica 100% seguros (máx 786 MHz), aplicando cirurgicamente apenas os pinos do hardware K36.

#### Falha 4: Analógicos Descentralizados e Eixos Invertidos
- **Causa:** O multiplexador analógico da placa V20 é fisicamente chaveado pelo **Pino 12** (`GPIO2_B4`), enquanto os DTBs comuns utilizavam o pino 11. Além disso, a deadzone padrão estava em 384 e o analógico direito estava com flags de inversão desnecessárias.
- **Solução:** Atualizado o nó `/odroidgo3-joypad`: AMUX Enable no pino 12, deadzone ajustada para 64, analógico esquerdo com inversão X/Y e analógico direito com mapeamento direto não invertido.

#### Falha 5: Áudio do Alto-falante Mudo / Inversão no Conector P2
- **Causa:** O conector mecânico P2 (3.5mm) desta revisão de placa possui uma chave de contato normalmente fechada (lógica inversa). O DTB padrão utilizava `simple-audio-card,hp-det-gpio = <195 22 1>` (`GPIO_ACTIVE_LOW`), fazendo com que o kernel Linux assumisse falsamente que havia fone plugado o tempo todo quando o conector estava vazio, mutando o alto-falante. Quando um fone de ouvido era inserido, o som saía no alto-falante!
- **Solução:** O pino de detecção de fone foi alterado para polaridade `GPIO_ACTIVE_HIGH` (`0`): `<195 22 0>`. Com isso, o alto-falante toca normalmente no menu e nos jogos, e ao plugar o fone, o alto-falante muta corretamente direcionando o áudio para o conector P2.

---

### 4. Como Usar em Qualquer Sistema (Omni36OS, DArkOSen, ArkOS)
1. Grave a imagem do sistema desejado no cartão micro SD.
2. Abra a partição **`BOOT`** (FAT32) que aparece no Windows.
3. Copie os seguintes arquivos da raiz deste repositório para a partição `BOOT`, substituindo se solicitado:
   - `rk3326-r36s-linux.dtb`
   - `rk3326-k36-linux.dtb`
   - `rg351v-uboot.dtb`
   - `rg351mp-uboot.dtb`
   - `rg351p-uboot.dtb`
   - `boot.ini`
4. Ejete com segurança e ligue no console.

---

## 🇺🇸 English

### 1. Overview
This repository provides the **definitive Device Tree Blob (DTB) solution** and boot configuration files for the R36S clone handheld revision physically marked as:
```text
R36S-V20 2025-05-18 2541
```
Commonly known in the retro handheld community as the **K36 panel revision**.

Before this project, users attempting to run modern RK3326 distributions faced:
- Red LED bricking on power-on.
- Black screen after the U-Boot bootloader splash.
- Immediate Linux kernel panic at 6.5 seconds:  
  `Kernel panic - not syncing: Attempted to kill init! exitcode=0x0000000b`.
- Severely drifting, off-center, or inverted analog sticks.

This project reverse-engineered the hardware layout, rebuilt the device trees using safe stock memory timings on 2025 clone bases, and calibrated the analog multiplexer, resulting in **100% verified hardware functionality** on both **Omni36OS** and **DArkOSen**.

---

### 2. Hardware Specifications & Pin Mapping
- **SoC:** Rockchip RK3326 (Quad-Core ARM Cortex-A35, Mali-G31 MP2 GPU).
- **Display Controller:** KD35T133 (MIPI-DSI 4-lanes, 640x480 @ 30 MHz, 370-byte DCS init sequence — Panel 8 compatible).
- **LCD Pinout:**
  - **Panel Reset:** `GPIO3_B7` (Pin 15, active-low) -> `<104 15 1>` *(unlike standard G80C clones which use pin 27)*.
  - **Panel Power Enable (`vcc18_lcd0`):** `GPIO0_B5` (Pin 13, active-high) -> `<94 13 0>` *(unlike standard clones which use pin 3)*.
- **Controls & Analog Sticks Pinout:**
  - **Analog Multiplexer Enable (AMUX Enable):** `GPIO2_B4` (Pin 12) -> `<195 12 1>` *(unlike standard clones which use pin 11)*.
  - **Deadzone:** `64`.
  - **Axis Orientation:**
    - Left Stick: Inverted X and Y (`invert-absx`, `invert-absy`).
    - Right Stick: Standard orientation (Up=Up, Down=Down, Left=Left, Right=Right).
  - **Button Labels:** `sw7 = GPIO BTN-Y`, `sw8 = GPIO BTN-X`.
- **DRAM & CPU Frequencies:**
  - **DMC / DDR3:** Safe stock timings (max 786 MHz, 528/666 MHz active).
  - **CPU:** Stock safe maximum 1512 MHz.

---

### 3. Technical Changelog & Issue Resolution

#### Issue 1: Red LED on Boot (U-Boot Failure)
- **Root Cause:** Clone boards read hardware ADC dividers and specifically request `rg351v-uboot.dtb`. If missing or invalid, U-Boot enters a panic state.
- **Fix:** Provided pre-patched `rg351v-uboot.dtb`, `rg351mp-uboot.dtb`, and `rg351p-uboot.dtb` with K36 reset pin 15 and enable pin 13.

#### Issue 2: Silent Black Screen
- **Root Cause:** Upstream `boot.ini` directed output to `console=/dev/ttyFIQ0` with `quiet splash`, silencing Linux errors.
- **Fix:** Set `console=tty1` to expose all kernel logs directly to the LCD.

#### Issue 3: SIGSEGV Kernel Panic (`exitcode=0x0000000b`)
- **Root Cause:** Legacy community K36 DTBs (such as ArkOS4Clone) contained aggressive DRAM overclocks (924 MHz and 1040 MHz). Under 64-bit arm64 Linux kernels, this caused memory corruption resulting in signal 11 (`SIGSEGV`) inside PID 1 (`systemd`) at 6.5 seconds.
- **Fix:** Rebased onto the verified 2025 clone tree (`G80C-MB V1.1-20250319 Panel 8`) with rock-solid factory RAM clocks, applying in-place byte patches exclusively to the K36 pins.

#### Issue 4: Analog Sticks Drift, Off-Center & Axis Inversion
- **Root Cause:** The board's analog multiplexer enable signal is physically wired to **Pin 12** (`GPIO2_B4`), whereas generic DTBs used pin 11. Generic deadzone was also set to 384, and the right stick had unwanted inversion flags.
- **Fix:** Patched `/odroidgo3-joypad`: enabled pin 12, set deadzone to 64, inverted left stick axes, and restored standard orientation for the right stick.

#### Issue 5: Silent Internal Speaker / Inverted Headphone Jack Detection (P2)
- **Root Cause:** The physical 3.5mm headphone jack on this motherboard revision uses a normally closed switch mechanism. The stock DTB set `simple-audio-card,hp-det-gpio = <195 22 1>` (`GPIO_ACTIVE_LOW`), causing the Linux ALSA driver to believe headphones were permanently plugged in when the jack was empty, completely muting the internal speaker. Plugging in headphones reversed the state and enabled the speaker.
- **Fix:** Patched the headphone detect pin polarity to `GPIO_ACTIVE_HIGH` (`0`): `<195 22 0>`. Now the internal speaker plays normally with no headphones connected, and automatically mutes when headphones are plugged in.

---

### 4. File Manifest

| File | Size | Purpose |
| :--- | :--- | :--- |
| **`rk3326-r36s-linux.dtb`** | 92,433 bytes | Linux kernel device tree with K36 display and calibrated controls. |
| **`rk3326-k36-linux.dtb`** | 92,433 bytes | Identical copy for OS distributions querying this filename. |
| **`rg351v-uboot.dtb`** | 59,519 bytes | U-Boot bootloader device tree with K36 pins (prevents red LED). |
| **`rg351mp-uboot.dtb`** | 59,519 bytes | U-Boot compatibility binary. |
| **`rg351p-uboot.dtb`** | 59,519 bytes | U-Boot compatibility binary. |
| **`boot.ini`** | 523 bytes | Verified boot configuration. |
| **`gerar_dtbs_k36.py`** | ~3 KB | Standalone Python script to reproduce or recompile the patch. |
| **`R36S_V20_2025-05-18_2541_K36_DTB_FIX.zip`** | ~88 KB | Complete ready-to-flash archive. |

---

## 5. Credits & Acknowledgements
- **Author & Hardware Architect:** Joel Ramalho ([@JoelRamalhoF](https://github.com/JoelRamalhoF))
- **Technical Co-pilot:** Antigravity (Google DeepMind)
- Tested and verified on physical hardware running **Omni36OS** and **DArkOSen**.

