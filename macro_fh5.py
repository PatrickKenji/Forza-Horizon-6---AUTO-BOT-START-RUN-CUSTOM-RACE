import os
import sys
import time
import numpy as np
import pyautogui
import cv2
import keyboard
import pydirectinput

# Desativar o fail-safe do PyAutoGUI para evitar que o macro pare se o mouse for movido para o canto da tela
pyautogui.FAILSAFE = False

def press_keyboard_key(key):
    """Pressiona uma tecla do teclado de forma compatível com jogos DirectX (DirectInput)."""
    try:
        pydirectinput.keyDown(key)
        time.sleep(0.15)  # Pequeno atraso para garantir o registro do input
        pydirectinput.keyUp(key)
    except Exception as e:
        print(f"Erro ao pressionar tecla {key}: {e}")

def press_gamepad_button(gamepad, button):
    """Pressiona um botão no controle Xbox virtual."""
    if gamepad is None:
        return
    try:
        import vgamepad as vg
        if button == 'x':
            btn = vg.XUSB_BUTTON.XUSB_GAMEPAD_X
        elif button == 'a':
            btn = vg.XUSB_BUTTON.XUSB_GAMEPAD_A
        else:
            return
            
        gamepad.press_button(button=btn)
        gamepad.update()
        time.sleep(0.15)
        gamepad.release_button(button=btn)
        gamepad.update()
    except Exception as e:
        print(f"Erro ao pressionar botão {button} no controle: {e}")

def set_acceleration(mode, gamepad, state):
    """Ativa ou desativa a aceleração contínua (tecla 'w' ou RT no controle)."""
    if mode == 'teclado':
        try:
            if state:
                pydirectinput.keyDown('w')
            else:
                pydirectinput.keyUp('w')
        except Exception as e:
            print(f"Erro ao controlar acelerador (teclado): {e}")
    else:
        if gamepad is not None:
            try:
                # 255 = Gatilho pressionado no máximo, 0 = Solto
                val = 255 if state else 0
                gamepad.right_trigger(value=val)
                gamepad.update()
            except Exception as e:
                print(f"Erro ao controlar acelerador (controle): {e}")

def match_template(screen, template):
    """Procura pelo template na imagem de tela atual e retorna o maior valor de confiança (0 a 1)."""
    if screen.shape[0] < template.shape[0] or screen.shape[1] < template.shape[1]:
        return 0.0
    res = cv2.matchTemplate(screen, template, cv2.TM_CCOEFF_NORMED)
    _, max_val, _, _ = cv2.minMaxLoc(res)
    return max_val

def calibrate():
    """Modo de calibração interativo para tirar fotos das 3 telas de referência."""
    print("\n" + "="*50)
    print("           MODO DE CALIBRAÇÃO DE IMAGENS             ")
    print("="*50)
    print("Recomendações importantes:")
    print("1. O jogo deve estar rodando na tela principal (Monitor 1).")
    print("2. Rode o jogo em modo Janela ou Janela Sem Bordas (Borderless).")
    print("3. Você pode usar as imagens que me enviou abertas em tela cheia no Monitor 1 para calibrar!")
    print("-"*50)

    # 1. Tela do Placar (Leaderboard)
    print("\n[TELA 1] Tela de Placar/Resultados da Corrida (onde aparece 'Reiniciar' com X)")
    print("-> Vá para essa tela e pressione a tecla 'F9' para capturar...")
    keyboard.wait('f9')
    time.sleep(0.5)
    screenshot = pyautogui.screenshot()
    img = cv2.cvtColor(np.array(screenshot), cv2.COLOR_RGB2BGR)
    
    print("-> Uma janela se abrirá. Use o mouse para desenhar um retângulo vermelho sobre a barra verde")
    print("   ou o título 'SP Farm' e pressione ENTER ou ESPAÇO para confirmar.")
    r = cv2.selectROI("Selecione a regiao para a Tela 1 (Placar)", img, fromCenter=False, showCrosshair=True)
    cv2.destroyAllWindows()
    
    if r[2] > 0 and r[3] > 0:
        crop = img[int(r[1]):int(r[1]+r[3]), int(r[0]):int(r[0]+r[2])]
        cv2.imwrite("template_leaderboard.png", crop)
        print("-> Tela 1 salva com sucesso como 'template_leaderboard.png'!")
    else:
        print("-> Calibração cancelada pelo usuário.")
        return False

    # 2. Tela de Confirmação (Popup)
    print("\n[TELA 2] Popup de Confirmação 'Reiniciar Evento' (onde aparece 'Sim' ou 'Não')")
    print("-> Vá para essa tela e pressione a tecla 'F9' para capturar...")
    keyboard.wait('f9')
    time.sleep(0.5)
    screenshot = pyautogui.screenshot()
    img = cv2.cvtColor(np.array(screenshot), cv2.COLOR_RGB2BGR)
    
    print("-> Desenhe o retângulo sobre a caixa amarela/verde de 'Reiniciar Evento' e confirme.")
    r = cv2.selectROI("Selecione a regiao para a Tela 2 (Confirmacao)", img, fromCenter=False, showCrosshair=True)
    cv2.destroyAllWindows()
    
    if r[2] > 0 and r[3] > 0:
        crop = img[int(r[1]):int(r[1]+r[3]), int(r[0]):int(r[0]+r[2])]
        cv2.imwrite("template_confirm.png", crop)
        print("-> Tela 2 salva com sucesso como 'template_confirm.png'!")
    else:
        print("-> Calibração cancelada pelo usuário.")
        return False

    # 3. Tela de Pré-Corrida (Menu)
    print("\n[TELA 3] Menu Pré-Corrida (onde tem o botão destacado 'Iniciar Evento de Corrida')")
    print("-> Vá para essa tela e pressione a tecla 'F9' para capturar...")
    keyboard.wait('f9')
    time.sleep(0.5)
    screenshot = pyautogui.screenshot()
    img = cv2.cvtColor(np.array(screenshot), cv2.COLOR_RGB2BGR)
    
    print("-> Desenhe o retângulo sobre o botão destacado verde/preto 'Iniciar Evento de Corrida' e confirme.")
    r = cv2.selectROI("Selecione a regiao para a Tela 3 (Pre-Corrida)", img, fromCenter=False, showCrosshair=True)
    cv2.destroyAllWindows()
    
    if r[2] > 0 and r[3] > 0:
        crop = img[int(r[1]):int(r[1]+r[3]), int(r[0]):int(r[0]+r[2])]
        cv2.imwrite("template_prerace.png", crop)
        print("-> Tela 3 salva com sucesso como 'template_prerace.png'!")
    else:
        print("-> Calibração cancelada pelo usuário.")
        return False

    print("\n" + "="*50)
    print("         CALIBRAÇÃO CONCLUÍDA COM SUCESSO!           ")
    print("="*50)
    print("Todas as 3 imagens de referência foram geradas.")
    return True

def run_macro(mode='teclado', threshold=0.85, auto_accel=True):
    """Loop principal do macro que monitora a tela e executa as ações em sequência."""
    if not (os.path.exists("template_leaderboard.png") and 
            os.path.exists("template_confirm.png") and 
            os.path.exists("template_prerace.png")):
        print("\n[ERRO] Imagens de referência não encontradas.")
        print("Por favor, execute a calibração (Opção 1) antes de iniciar o macro.")
        return

    # Carregar templates
    temp_leaderboard = cv2.imread("template_leaderboard.png")
    temp_confirm = cv2.imread("template_confirm.png")
    temp_prerace = cv2.imread("template_prerace.png")

    # Tentar inicializar o controle virtual se selecionado
    gamepad = None
    if mode == 'controle':
        try:
            import vgamepad as vg
            gamepad = vg.VX360Gamepad()
            print("\n[OK] Controle virtual Xbox 360 inicializado com sucesso!")
        except ImportError:
            print("\n[AVISO] Biblioteca 'vgamepad' ou driver 'ViGEmBus' não encontrados.")
            print("Usando o modo TECLADO como alternativa automática.")
            mode = 'teclado'

    print("\n" + "="*50)
    print(f"    MACRO INICIADO - MODO: {mode.upper()} | ACELERAÇÃO: {'ATIVADA' if auto_accel else 'DESATIVADA'}")
    print("="*50)
    print("-> Pressione a tecla 'ESC' a qualquer momento para PARAR o macro.")
    print("Monitorando a tela...")
    print("-"*50)

    # Registros de última execução para evitar cliques múltiplos (cooldowns)
    last_action_time = {
        'leaderboard': 0.0,
        'confirm': 0.0,
        'prerace': 0.0
    }

    # Tempos mínimos de espera em segundos entre ativações
    cooldowns = {
        'leaderboard': 5.0,  # Espera 5 segundos para o placar sumir
        'confirm': 4.0,      # Espera 4 segundos para o popup sumir
        'prerace': 15.0      # Espera 15 segundos (carregamento e início da corrida)
    }

    active = True
    is_accelerating = False

    # Função interna para desligar o macro via tecla ESC
    def stop_macro(e):
        nonlocal active
        if e.name == 'esc':
            active = False

    keyboard.on_press(stop_macro)

    try:
        while active:
            # Capturar tela principal
            screenshot = pyautogui.screenshot()
            screen_img = cv2.cvtColor(np.array(screenshot), cv2.COLOR_RGB2BGR)
            current_time = time.time()
            menu_detected = False

            # 1. Verificar Tela 1: Leaderboard (Placar)
            if current_time - last_action_time['leaderboard'] > cooldowns['leaderboard']:
                match_val = match_template(screen_img, temp_leaderboard)
                if match_val > threshold:
                    menu_detected = True
                    if auto_accel and is_accelerating:
                        print(f"[{time.strftime('%H:%M:%S')}] Soltando acelerador (Menu detectado).")
                        set_acceleration(mode, gamepad, False)
                        is_accelerating = False

                    print(f"[{time.strftime('%H:%M:%S')}] Tela 1 (Placar) detectada! Confiança: {match_val:.2f} -> Pressionando X (Reiniciar)")
                    if mode == 'teclado':
                        press_keyboard_key('x')
                    else:
                        press_gamepad_button(gamepad, 'x')
                    last_action_time['leaderboard'] = current_time
                    time.sleep(1.0)  # Pequeno atraso para transição de tela
                    continue

            # 2. Verificar Tela 2: Confirm Popup (Confirmação)
            if current_time - last_action_time['confirm'] > cooldowns['confirm']:
                match_val = match_template(screen_img, temp_confirm)
                if match_val > threshold:
                    menu_detected = True
                    if auto_accel and is_accelerating:
                        print(f"[{time.strftime('%H:%M:%S')}] Soltando acelerador (Menu detectado).")
                        set_acceleration(mode, gamepad, False)
                        is_accelerating = False

                    print(f"[{time.strftime('%H:%M:%S')}] Tela 2 (Confirmação) detectada! Confiança: {match_val:.2f} -> Pressionando A (Sim)")
                    if mode == 'teclado':
                        press_keyboard_key('enter')
                    else:
                        press_gamepad_button(gamepad, 'a')
                    last_action_time['confirm'] = current_time
                    time.sleep(1.0)
                    continue

            # 3. Verificar Tela 3: Pre-race Menu (Pré-Corrida)
            if current_time - last_action_time['prerace'] > cooldowns['prerace']:
                match_val = match_template(screen_img, temp_prerace)
                if match_val > threshold:
                    menu_detected = True
                    if auto_accel and is_accelerating:
                        print(f"[{time.strftime('%H:%M:%S')}] Soltando acelerador (Menu detectado).")
                        set_acceleration(mode, gamepad, False)
                        is_accelerating = False

                    print(f"[{time.strftime('%H:%M:%S')}] Tela 3 (Menu Pré-Corrida) detectada! Confiança: {match_val:.2f} -> Pressionando A (Iniciar)")
                    if mode == 'teclado':
                        press_keyboard_key('enter')
                    else:
                        press_gamepad_button(gamepad, 'a')
                    last_action_time['prerace'] = current_time
                    print("Corrida iniciada! Aguardando o carregamento da prova...")
                    time.sleep(5.0)  # Evita leituras durante o fade-out/carregamento inicial
                    continue

            # Se a aceleração automática estiver ativada, nenhum menu for detectado, e não estivermos acelerando:
            if auto_accel and not menu_detected and not is_accelerating:
                print(f"[{time.strftime('%H:%M:%S')}] Pista livre detectada. Ativando acelerador automático...")
                set_acceleration(mode, gamepad, True)
                is_accelerating = True

            # Reduzir uso de CPU
            time.sleep(0.15)

    except Exception as e:
        print(f"\n[ERRO] Ocorreu uma exceção no loop do macro: {e}")
    finally:
        keyboard.unhook_all()
        # Garantir que o acelerador seja solto ao parar o macro
        if auto_accel and is_accelerating:
            set_acceleration(mode, gamepad, False)
        print("\n" + "="*50)
        print("                 MACRO FINALIZADO                     ")
        print("="*50)

auto_accelerate = True  # Variável global para controle de aceleração

def main():
    global auto_accelerate
    while True:
        status_acel = "ATIVADA" if auto_accelerate else "DESATIVADA"
        print("\n" + "="*50)
        print("          MACRO DE REINICIALIZAÇÃO - FH5             ")
        print("="*50)
        print("1. Calibrar Imagens de Referência (Selecionar Telas)")
        print("2. Iniciar Macro (Modo TECLADO - Recomendado)")
        print("3. Iniciar Macro (Modo CONTROLE XBOX VIRTUAL)")
        print(f"4. Alternar Aceleração Automática (Atual: {status_acel})")
        print("5. Sair")
        print("="*50)
        
        opcao = input("Selecione uma opção (1-5): ").strip()
        
        if opcao == '1':
            calibrate()
        elif opcao == '2':
            run_macro(mode='teclado', auto_accel=auto_accelerate)
        elif opcao == '3':
            run_macro(mode='controle', auto_accel=auto_accelerate)
        elif opcao == '4':
            auto_accelerate = not auto_accelerate
            print(f"\nAceleração automática alterada para: {'ATIVADA' if auto_accelerate else 'DESATIVADA'}")
        elif opcao == '5':
            print("\nObrigado por usar o macro. Até mais!")
            sys.exit(0)
        else:
            print("\nOpção inválida! Digite um número de 1 a 5.")

if __name__ == "__main__":
    main()
