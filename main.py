import streamlit as st
from datetime import datetime, date
import json
import os

# --- Configurações da Página ---
st.set_page_config(page_title="Agendamento Barbearia", page_icon="✂️")

# --- Persistência de Dados (Arquivo JSON) ---
ARQUIVO_DADOS = "agendamentos.json"

def carregar_agendamentos():
    if os.path.exists(ARQUIVO_DADOS):
        with open(ARQUIVO_DADOS, "r") as f:
            return json.load(f)
    return {}

def salvar_agendamento(data, horario):
    agendamentos = carregar_agendamentos()
    data_str = str(data)
    if data_str not in agendamentos:
        agendamentos[data_str] = []
    agendamentos[data_str].append(horario)
    with open(ARQUIVO_DADOS, "w") as f:
        json.dump(agendamentos, f)

# --- Dados da Barbearia ---
SEU_NUMERO_WHATSAPP = "5571996886414"
HORARIOS_TODOS = ["08:00", "08:30", "09:00", "09:30", "10:00", "10:30", "11:00", "11:30",
                  "13:00", "13:30", "14:00", "14:30", "15:00", "15:30", "16:00", "16:30", "17:00", "17:30"]
SERVICOS = ["BARBA R$15", "CABELO R$25", "BARBA+CABELO R$35", "NEVOU R$100", "LUZES R$80", "PEZINHO R$10", "PIGMENTAÇÃO R$10"]

st.title("✂️ Bigode Barber")
st.subheader("Agende seu horário com facilidade")

# --- Formulário de Agendamento ---
with st.container():
    st.write("---")
    nome_cliente = st.text_input("Seu Nome:")
    
    col1, col2 = st.columns(2)
    with col1:
        data_agendamento = st.date_input("Escolha a Data", min_value=date.today())
    
    # --- Lógica de Filtro de Horários Ocupados ---
    agendamentos_existentes = carregar_agendamentos()
    data_selecionada_str = str(data_agendamento)
    
    # Pegamos os horários já ocupados para o dia escolhido
    horarios_ocupados = agendamentos_existentes.get(data_selecionada_str, [])
    
    # Criamos a lista de horários disponíveis (apenas os que não estão ocupados)
    horarios_disponiveis = [h for h in HORARIOS_TODOS if h not in horarios_ocupados]

    with col2:
        if horarios_disponiveis:
            horario_escolhido = st.selectbox("Escolha o Horário", horarios_disponiveis)
        else:
            st.error("Desculpe, não há horários disponíveis para este dia.")
            horario_escolhido = None

    servico_escolhido = st.selectbox("Qual serviço deseja?", SERVICOS)
    data_formatada = data_agendamento.strftime("%d/%m/%Y")

    st.write("---")
    
    if horario_escolhido and nome_cliente:
        # Criação da mensagem do WhatsApp
        msg = f"Olá! Gostaria de agendar um horário.%0A%0A*Nome:* {nome_cliente}%0A*Data:* {data_formatada}%0A*Horário:* {horario_escolhido}%0A*Serviço:* {servico_escolhido}"
        link_whatsapp = f"https://wa.me/{SEU_NUMERO_WHATSAPP}?text={msg}"

        # Botão que salva no sistema e redireciona
        if st.button("✅ Confirmar e Ir para WhatsApp"):
            salvar_agendamento(data_agendamento, horario_escolhido)
            st.success(f"Agendamento para {horario_escolhido} registrado!")
            st.markdown(f'<meta http-equiv="refresh" content="2;url={link_whatsapp}">', unsafe_allow_stdio=True)
            st.info("Redirecionando para o WhatsApp...")
    else:
        st.warning("Preencha seu nome e escolha um horário disponível.")