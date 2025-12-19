import streamlit as st
from datetime import datetime, date
import json
import os
import pandas as pd
import urllib.parse

# --- Configurações da Página ---
st.set_page_config(page_title="Bigode Barber", page_icon="✂️", layout="centered")

# --- Arquivo de Banco de Dados Local ---
ARQUIVO_DADOS = "agendamentos_detalhados.json"

# --- Funções de Gerenciamento de Dados ---
def carregar_agendamentos():
    """Carrega os dados do JSON com tratamento de erro para arquivo vazio."""
    if os.path.exists(ARQUIVO_DADOS):
        try:
            with open(ARQUIVO_DADOS, "r") as f:
                conteudo = f.read().strip()
                return json.loads(conteudo) if conteudo else {}
        except (json.JSONDecodeError, Exception):
            return {}
    return {}

def salvar_agendamento(data, horario, nome, servico):
    """Salva o agendamento vinculando cliente e serviço ao horário."""
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
    """Remove um agendamento e libera o horário novamente."""
    agendamentos = carregar_agendamentos()
    if data_str in agendamentos and horario in agendamentos[data_str]:
        del agendamentos[data_str][horario]
        if not agendamentos[data_str]:
            del agendamentos[data_str]
        with open(ARQUIVO_DADOS, "w") as f:
            json.dump(agendamentos, f, indent=4)
        return True
    return False

# --- Configurações da Barbearia ---
SEU_NUMERO_WHATSAPP = "5571996886414"
HORARIOS_TODOS = [
    "08:00", "08:30", "09:00", "09:30", "10:00", "10:30", "11:00", "11:30",
    "13:00", "13:30", "14:00", "14:30", "15:00", "15:30", "16:00", "16:30", 
    "17:00", "17:30", "18:00", "18:30"
]
SERVICOS = ["BARBA R$15", "CABELO R$25", "BARBA+CABELO R$35", "NEVOU COMPLETO R$100", "LUZES R$80", "PEZINHO R$10, "CORTE+PIGMENTAÇÃO R$35",]

# --- Área do Cliente ---
st.title("✂️ Bigode Barber")
st.subheader("Agende seu horário com facilidade")

with st.container():
    st.write("---")
    nome_cliente = st.text_input("Seu Nome:")
    
    col1, col2 = st.columns(2)
    with col1:
        data_agendamento = st.date_input("Escolha a Data", min_value=date.today())
    
    # Filtragem de horários disponíveis
    dados_atuais = carregar_agendamentos()
    data_sel_str = str(data_agendamento)
    ocupados = dados_atuais.get(data_sel_str, {}).keys()
    horarios_disponiveis = [h for h in HORARIOS_TODOS if h not in ocupados]

    with col2:
        if horarios_disponiveis:
            horario_escolhido = st.selectbox("Horários Disponíveis", horarios_disponiveis)
        else:
            st.error("Agenda lotada para este dia!")
            horario_escolhido = None

    servico_escolhido = st.selectbox("Qual serviço deseja?", SERVICOS)

    st.write("---")

    if nome_cliente and horario_escolhido:
        if st.button("✅ Confirmar Agendamento"):
            # 1. Salva no arquivo local
            salvar_agendamento(data_agendamento, horario_escolhido, nome_cliente, servico_escolhido)
            
            st.success(f"Reservado para {data_agendamento.strftime('%d/%m/%Y')} às {horario_escolhido}!")
            
            # 2. Prepara link do WhatsApp codificado
            msg_whatsapp = (
                f"Olá! Gostaria de confirmar meu agendamento.\n\n"
                f"*Nome:* {nome_cliente}\n"
                f"*Data:* {data_agendamento.strftime('%d/%m/%Y')}\n"
                f"*Horário:* {horario_escolhido}\n"
                f"*Serviço:* {servico_escolhido}"
            )
            texto_codificado = urllib.parse.quote(msg_whatsapp)
            link_final = f"https://wa.me/{SEU_NUMERO_WHATSAPP}?text={texto_codificado}"
            
            # 3. Botão visual de redirecionamento
            st.markdown(f"""
                <a href="{link_final}" target="_blank" style="text-decoration: none;">
                    <div style="background-color: #25D366; color: white; padding: 15px; text-align: center; border-radius: 8px; font-weight: bold; font-size: 18px; margin-top: 10px;">
                        🚀 CLIQUE AQUI PARA FINALIZAR NO WHATSAPP
                    </div>
                </a>
            """, unsafe_allow_html=True)
    else:
        st.warning("Preencha seu nome para habilitar o agendamento.")

st.write("")
st.write("")

# --- Painel do Administrador ---
with st.expander("🔐 Painel do Administrador"):
    senha = st.text_input("Senha de acesso", type="password")
    if senha == "admin123":
        st.subheader("📋 Agenda de Clientes")
        
        todos_dados = carregar_agendamentos()
        if todos_dados:
            # Gerar Tabela
            lista_tabela = []
            for d, horas in todos_dados.items():
                for h, info in horas.items():
                    lista_tabela.append({
                        "Data": d,
                        "Hora": h,
                        "Cliente": info['cliente'],
                        "Serviço": info['servico']
                    })
            
            df = pd.DataFrame(lista_tabela).sort_values(by=["Data", "Hora"])
            st.dataframe(df, use_container_width=True, hide_index=True)
            
            # Seção de Cancelamento
            st.write("---")
            st.subheader("🗑️ Cancelar Horário")
            c1, c2 = st.columns(2)
            with c1:
                dia_canc = st.selectbox("Selecione o Dia", sorted(list(todos_dados.keys())))
            with c2:
                hora_canc = st.selectbox("Selecione a Hora", sorted(list(todos_dados[dia_canc].keys())))
            
            if st.button("🔴 Excluir Agendamento"):
                if excluir_agendamento(dia_canc, hora_canc):
                    st.success("Horário liberado!")
                    st.rerun()
        else:
            st.info("Ainda não há agendamentos registrados.")

