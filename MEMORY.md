# MEMÓRIA DO PROJETO - OMNI36OS & PAINEL K36 (R36S V20 2025 05 18 2541)

## 1. Contexto e Objetivo
- **Console / Placa**: R36S placa `v20 2025 05 18 2541` (revisão clone baseada no hardware K36).
- **Sistema Operacional Alvo**: Omni36OS (baseado em ArkOS, otimizado para PortMaster).
- **Conquistas Validadas**:
  1. *LED vermelho*: Corrigido (U-Boot carrega com sucesso os DTBs patched).
  2. *Display U-Boot*: **100% FUNCIONANDO!** O console exibiu a logo do Omni36OS ("Carregando...") nítida, com cores perfeitas e na orientação correta (Foto 1).

## 2. Diagnóstico do Kernel Panic (Foto 3 e 4)
- **Erro apresentado nas fotos**:
  `[ 6.550071] ---[ end Kernel panic - not syncing: Attempted to kill init! exitcode=0x0000000b ]---`
- **Causa Raiz Identificada**:
  - `exitcode=0x0000000b` corresponde ao sinal 11 do Unix (`SIGSEGV` / falha de segmentação de memória) no processo `init` (`systemd`).
  - O arquivo `rk3326-k36-linux.dtb` original do ArkOS4Clone continha perfis extremos de overclock não suportados em ambiente arm64 estável:
    - DRAM (controlador de memória DMC) configurado com frequências de 924 MHz e 1040 MHz (stock do RK3326 é 666/786 MHz).
    - CPU com overclock até 1.608 GHz (stock é 1.248/1.512 GHz).
    - Tensões de reguladores PMIC alteradas.
  - Ao carregar o `systemd` em 64 bits, a instabilidade da memória RAM provocava corrupção de dados e o encerramento fatal do `init` em 6.55 segundos.

## 3. Solução Definitiva Desenvolvida (DTB Oficial Clone 2025 Patcheado)
- **Base utilizada**: DTB oficial da família clone 2025 presente no Omni36OS:
  `dtb/clone/G80C-MB V1.1-20250319 Panel 8/rk3326-r36s-linux.dtb` (92.433 bytes).
  - Tabela de memória DRAM 100% stock e segura (máx 786 MHz, operação a 528/666 MHz).
  - Frequências de CPU estáveis (máx 1.512 GHz).
  - Inicialização de display idêntica à do K36 (controlador KD35T133, 370 bytes de sequência DCS).
- **Patches in-place aplicados nos pinos K36**:
  1. *Panel Reset GPIO*: Offset 37788 alterado de `<104 27 1>` para `<104 15 1>` (GPIO3_B7 pino 15, active-low).
  2. *Panel Enable GPIO (`vcc18_lcd0`)*: Offset 65232 alterado de `<104 3 0>` para `<94 13 0>` (GPIO0_B5 pino 13, active-high).
  3. *Pinctrl `vcc18-lcd-n`*: Offset 59896 alterado de `[3, 3, 0, 182]` para `[0, 13, 0, 182]`.
  4. *Pinctrl `btn-pins`*: Offset 60300 alterado para liberar o pino 15 (substituído por 27).
- **Validação**: Testado e verificado via biblioteca `fdt` em Python; preservou a integridade de 92.433 bytes.
- **Distribuição**: Gravado em todas as variantes na raiz (`rk3326-r36s-linux.dtb`, `rk3326-k36-linux.dtb`, etc.).

## 4. Configuração de Boot (`boot.ini`)
- `bootargs`: Configurado com `console=tty1` para visibilidade na tela LCD, parâmetros stock de integridade (`fsck.repair=yes net.ifnames=0 usbcore.old_scheme_first=1`), frequências seguras (`boot_cpufreq=1296 max_cpufreq=1512`), mantendo terminadores de linha Unix (LF).

## 5. Como Funciona a Instalação e Próximo Passo
1. O console liga e exibe a logo do Omni36OS ("Carregando...").
2. O Kernel Linux inicializa de forma estável (sem crash de memória / SIGSEGV).
3. O `firstboot.sh` executa a Etapa 1 (~5s): particiona o SD e reinicia automaticamente o console.
4. No Boot 2, o sistema inicia a Etapa 2 e entra na **tela azul com a barra de progresso de expansão do EasyROMs** (Foto 2).
