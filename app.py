import streamlit as st
from datetime import datetime, date
import json
import os

# --- Configurações da Página ---
st.set_page_config(page_title="Bigode Barber", page_icon="✂️")

# --- Caminho do Arquivo de Dados ---
ARQUIVO_DADOS = "agendamentos.json"

# --- Funções de Persistência ---
def carregar_agendamentos():
    """Lê o arquivo JSON e trata erros de arquivo vazio ou inexistente."""
    if os.path.exists(ARQUIVO_DADOS):
        try:
            with open(ARQUIVO_DADOS, "r") as f:
                conteudo = f.read().strip()
                if not conteudo:
                    return {}
                return json.loads(conteudo)
        except (json.JSONDecodeError, Exception):
            return {}
    return {}

def salvar_agendamento(data, horario):
    """Adiciona o novo agendamento ao arquivo JSON."""
    agendamentos = carregar_agendamentos()
    data_str = str(data)
    
    if data_str not in agendamentos:
        agendamentos[data_str] = []
    
    if horario not in agendamentos[data_str]:
        agendamentos[data_str].append(horario)
        
    with open(ARQUIVO_DADOS, "w") as f:
        json.dump(agendamentos, f, indent=4)

# --- Dados da Barbearia ---
SEU_NUMERO_WHATSAPP = "5571996886414"
# Lista completa de horários
HORARIOS_TODOS = [
    "08:00", "08:30", "09:00", "09:30", "10:00", "10:30", "11:00", "11:30",
    "12:00", "12:30", "13:00", "13:30", "14:00", "14:30", "15:00", "15:30", 
    "16:00", "16:30", "17:00", "17:30", "18:00", "18:30", "19:00", "19:30"
]
SERVICOS = [
    "BARBA R$15", "CABELO R$25", "BARBA+CABELO R$35", 
    "NEVOU R$100", "LUZES R$80", "PEZINHO R$10", "PIGMENTAÇÃO R$10"
]

# --- Interface ---
st.title("✂️ Bigode Barber")
st.subheader("Agende seu horário com facilidade")

with st.container():
    st.write("---")
    nome_cliente = st.text_input("Seu Nome:")
    
    col1, col2 = st.columns(2)
    
    with col1:
        data_agendamento = st.date_input("Escolha a Data", min_value=date.today())
    
    # --- Lógica de Disponibilidade ---
    agendamentos_existentes = carregar_agendamentos()
    data_sel_str = str(data_agendamento)
    ocupados = agendamentos_existentes.get(data_sel_str, [])
    
    # Filtra apenas horários que NÃO estão no arquivo JSON para aquela data
    horarios_disponiveis = [h for h in HORARIOS_TODOS if h not in ocupados]

    with col2:
        if horarios_disponiveis:
            horario_escolhido = st.selectbox("Horários Disponíveis", horarios_disponiveis)
        else:
            st.error("Lotado! Escolha outro dia.")
            horario_escolhido = None

    servico_escolhido = st.selectbox("Qual serviço deseja?", SERVICOS)

    st.write("---")

    if nome_cliente and horario_escolhido:
        # Formatação para o Zap
        data_pt = data_agendamento.strftime("%d/%m/%Y")
        msg = (f"Olá! Gostaria de agendar um horário.%0A%0A"
               f"*Nome:* {nome_cliente}%0A"
               f"*Data:* {data_pt}%0A"
               f"*Horário:* {horario_escolhido}%0A"
               f"*Serviço:* {servico_escolhido}")
        
        link_whatsapp = f"https://wa.me/{SEU_NUMERO_WHATSAPP}?text={msg}"

        if st.button("✅ Confirmar Agendamento"):
            # 1. Salva no arquivo para bloquear o próximo
            salvar_agendamento(data_agendamento, horario_escolhido)
            
            # 2. Feedback visual
            st.success(f"Reservado para {data_pt} às {horario_escolhido}!")
            
            # 3. Link para o WhatsApp
            st.markdown(f"""
                <a href="{link_whatsapp}" target="_blank" style="text-decoration: none;">
                    <div style="background-color: #25D366; color: white; padding: 10px; text-align: center; border-radius: 5px; font-weight: bold;">
                        CLIQUE AQUI PARA FINALIZAR NO WHATSAPP
                    </div>
                </a>
            """, unsafe_allow_html=True)
    else:
        st.info("Preencha seu nome e escolha um horário para habilitar o agendamento.")

# --- Área do Administrador (Opcional - Apenas para você ver quem marcou) ---
with st.expander("Visualizar Agenda (Admin)"):
    senha = st.text_input("Senha de acesso", type="password")
    if senha == "123": # Altere sua senha aqui
        dados = carregar_agendamentos()
        if dados:
            st.write(dados)
        else:
            st.write("Nenhum agendamento ainda.")
