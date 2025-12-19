import streamlit as st
from datetime import datetime, date
import json
import os
import pandas as pd

# --- Configurações da Página ---
st.set_page_config(page_title="Bigode Barber", page_icon="✂️")

ARQUIVO_DADOS = "agendamentos_detalhados.json"

# --- Funções de Dados ---
def carregar_agendamentos():
    if os.path.exists(ARQUIVO_DADOS):
        try:
            with open(ARQUIVO_DADOS, "r") as f:
                return json.load(f)
        except: return {}
    return {}

def salvar_agendamento(data, horario, nome, servico):
    agendamentos = carregar_agendamentos()
    data_str = str(data)
    if data_str not in agendamentos:
        agendamentos[data_str] = {}
    
    agendamentos[data_str][horario] = {
        "cliente": nome,
        "servico": servico,
        "data_registro": datetime.now().strftime("%d/%m/%Y %H:%M")
    }
    with open(ARQUIVO_DADOS, "w") as f:
        json.dump(agendamentos, f, indent=4)

def excluir_agendamento(data_str, horario):
    agendamentos = carregar_agendamentos()
    if data_str in agendamentos and horario in agendamentos[data_str]:
        del agendamentos[data_str][horario]
        # Se o dia ficar vazio, removemos a data também
        if not agendamentos[data_str]:
            del agendamentos[data_str]
        with open(ARQUIVO_DADOS, "w") as f:
            json.dump(agendamentos, f, indent=4)
        return True
    return False

# --- Configurações da Barbearia ---
SEU_NUMERO_WHATSAPP = "5571996886414"
HORARIOS_TODOS = ["08:00", "08:30", "09:00", "09:30", "10:00", "10:30", "11:00", "11:30", 
                  "13:00", "13:30", "14:00", "14:30", "15:00", "15:30", "16:00", "16:30", "17:00"]
SERVICOS = ["BARBA R$15", "CABELO R$25", "BARBA+CABELO R$35", "NEVOU R$100", "PEZINHO R$10"]

# --- Interface do Cliente ---
st.title("✂️ Bigode Barber")
st.subheader("Agende seu horário")

nome_cliente = st.text_input("Seu Nome:")
col1, col2 = st.columns(2)

with col1:
    data_agendamento = st.date_input("Data", min_value=date.today())

# Lógica de Horários Disponíveis
dados = carregar_agendamentos()
data_sel_str = str(data_agendamento)
ocupados = dados.get(data_sel_str, {}).keys()
disponiveis = [h for h in HORARIOS_TODOS if h not in ocupados]

with col2:
    horario_escolhido = st.selectbox("Horário", disponiveis) if disponiveis else st.error("Lotado")

servico_escolhido = st.selectbox("Serviço", SERVICOS)

if st.button("✅ Confirmar Agendamento") and nome_cliente and horario_escolhido:
    salvar_agendamento(data_agendamento, horario_escolhido, nome_cliente, servico_escolhido)
    st.success("Reservado com sucesso!")
    
    msg = f"Olá! Agendei um horário.%0A*Nome:* {nome_cliente}%0A*Data:* {data_agendamento.strftime('%d/%m/%Y')}%0A*Hora:* {horario_escolhido}"
    st.markdown(f'[👉 CLIQUE AQUI PARA FINALIZAR NO WHATSAPP](https://wa.me/{SEU_NUMERO_WHATSAPP}?text={msg})')

st.write("---")

# --- Painel do Administrador Melhores ---
with st.expander("🔐 Painel do Administrador"):
    senha = st.text_input("Senha", type="password")
    if senha == "admin123":
        st.subheader("📋 Gestão de Clientes")
        
        todos_dados = carregar_agendamentos()
        if todos_dados:
            # Criar lista para DataFrame
            lista = []
            for d, horas in todos_dados.items():
                for h, info in horas.items():
                    lista.append({"Data": d, "Hora": h, "Cliente": info['cliente'], "Serviço": info['servico']})
            
            df = pd.DataFrame(lista).sort_values(["Data", "Hora"])
            st.table(df) # Exibe lista simplificada
            
            st.write("---")
            st.subheader("🗑️ Cancelar Horário")
            col_d, col_h = st.columns(2)
            with col_d:
                data_cancelar = st.selectbox("Escolha o dia", list(todos_dados.keys()))
            with col_h:
                horarios_da_data = list(todos_dados[data_cancelar].keys())
                hora_cancelar = st.selectbox("Escolha a hora", horarios_da_data)
            
            if st.button("🔴 Excluir Agendamento"):
                if excluir_agendamento(data_cancelar, hora_cancelar):
                    st.success("Horário liberado!")
                    st.rerun() # Atualiza a tela para sumir da lista
        else:
            st.info("Nenhum agendamento registrado.")
