import streamlit as st
from datetime import datetime, date
import json
import os
import pandas as pd

# --- Configurações da Página ---
st.set_page_config(page_title="Bigode Barber Admin", page_icon="✂️", layout="centered")

# --- Caminho do Arquivo de Dados ---
ARQUIVO_DADOS = "agendamentos_detalhados.json"

# --- Funções de Persistência ---
def carregar_agendamentos():
    if os.path.exists(ARQUIVO_DADOS):
        try:
            with open(ARQUIVO_DADOS, "r") as f:
                conteudo = f.read().strip()
                return json.loads(conteudo) if conteudo else {}
        except:
            return {}
    return {}

def salvar_agendamento(data, horario, nome, servico):
    agendamentos = carregar_agendamentos()
    data_str = str(data)
    
    if data_str not in agendamentos:
        agendamentos[data_str] = {}
    
    # Salva os detalhes usando o horário como chave
    agendamentos[data_str][horario] = {
        "cliente": nome,
        "servico": servico,
        "data_registro": datetime.now().strftime("%d/%m/%Y %H:%M")
    }
        
    with open(ARQUIVO_DADOS, "w") as f:
        json.dump(agendamentos, f, indent=4)

# --- Dados da Barbearia ---
SEU_NUMERO_WHATSAPP = "5571996886414"
HORARIOS_TODOS = [
    "08:00", "08:30", "09:00", "09:30", "10:00", "10:30", "11:00", "11:30",
    "13:00", "13:30", "14:00", "14:30", "15:00", "15:30", "16:00", "16:30", 
    "17:00", "17:30", "18:00", "18:30"
]
SERVICOS = ["BARBA R$15", "CABELO R$25", "BARBA+CABELO R$35", "NEVOU R$100", "PEZINHO R$10"]

# --- Interface de Agendamento (Cliente) ---
st.title("✂️ Bigode Barber")
st.subheader("Agende seu horário")

nome_cliente = st.text_input("Seu Nome:")
col1, col2 = st.columns(2)

with col1:
    data_agendamento = st.date_input("Data", min_value=date.today())

# Lógica de Horários Ocupados
dados_atuais = carregar_agendamentos()
data_sel_str = str(data_agendamento)
horarios_ocupados = dados_atuais.get(data_sel_str, {}).keys()
horarios_disponiveis = [h for h in HORARIOS_TODOS if h not in horarios_ocupados]

with col2:
    if horarios_disponiveis:
        horario_escolhido = st.selectbox("Horário", horarios_disponiveis)
    else:
        st.error("Sem horários!")
        horario_escolhido = None

servico_escolhido = st.selectbox("Serviço", SERVICOS)

if st.button("✅ Confirmar Agendamento") and nome_cliente and horario_escolhido:
    salvar_agendamento(data_agendamento, horario_escolhido, nome_cliente, servico_escolhido)
    st.success("Reservado!")
    
    # Gerar link Whatsapp
    msg = f"Olá! Agendei um horário.%0A*Nome:* {nome_cliente}%0A*Data:* {data_agendamento.strftime('%d/%m/%Y')}%0A*Hora:* {horario_escolhido}"
    link = f"https://wa.me/{SEU_NUMERO_WHATSAPP}?text={msg}"
    st.markdown(f'[👉 CLIQUE AQUI PARA ABRIR O WHATSAPP]({link})')

st.write("---")

# --- AREA DO ADMINISTRADOR MELHORADA ---
with st.expander("🔐 Painel do Administrador"):
    senha = st.text_input("Senha Admin", type="password")
    if senha == "admin123":
        st.subheader("📋 Agenda Completa")
        
        todos_dados = carregar_agendamentos()
        
        if todos_dados:
            lista_para_tabela = []
            
            # Organiza os dados para o formato de tabela (DataFrame)
            for data, horarios in todos_dados.items():
                for hora, info in horarios.items():
                    lista_para_tabela.append({
                        "Data": data,
                        "Horário": hora,
                        "Cliente": info['cliente'],
                        "Serviço": info['servico']
                    })
            
            df = pd.DataFrame(lista_para_tabela)
            
            # Ordenar por data e horário
            df = df.sort_values(by=["Data", "Horário"])
            
            # Exibe a tabela estilizada
            st.dataframe(df, use_container_width=True, hide_index=True)
            
            # Filtro por data
            st.write("---")
            data_filtro = st.date_input("Filtrar por dia específico", value=date.today())
            if str(data_filtro) in todos_dados:
                st.write(f"**Agenda para {data_filtro.strftime('%d/%m/%Y')}:**")
                for h, i in todos_dados[str(data_filtro)].items():
                    st.info(f"⏰ **{h}** - 👤 {i['cliente']} ({i['servico']})")
            else:
                st.write("Nenhum agendamento para este dia.")
        else:
            st.info("A agenda está vazia.")
