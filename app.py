import re
import streamlit as st

st.set_page_config(page_title="Formatador RDO - Consórcio", page_icon="🏗️", layout="centered")

st.title("🏗️ Formatador de Mensagens RDO")
st.markdown("Cole as mensagens do WhatsApp para gerar a lista padronizada `Rua - Estaca - Lado - Atividade`.")

texto_bruto = st.text_area("Mensagens brutas do WhatsApp:", height=250, placeholder="Cole aqui o texto enviado no grupo...")

def processar_rdo(texto):
    if not texto.strip():
        return []

    texto_limpo = texto.replace('\xa0', ' ')
    blocos_brutos = re.split(r'(Lote\s*[\d\.]+)', texto_limpo, flags=re.IGNORECASE)
    
    blocos = []
    temp = ""
    for b in blocos_brutos:
        temp += b
        if re.search(r'Lote\s*[\d\.]+', b, re.IGNORECASE):
            blocos.append(temp.strip())
            temp = ""
    if temp.strip():
        blocos.append(temp.strip())

    linhas_finais = []

    for bloco in blocos:
        if not bloco or len(bloco) < 10:
            continue

        rua_match = re.search(r'(Rua\s+[^\n\r]+)', bloco, re.IGNORECASE)
        rua = rua_match.group(1).strip() if rua_match else "Rua não informada"
        rua = re.sub(r'Rua\s+oliveira', 'Rua Oliveira', rua, flags=re.IGNORECASE)

        estaca_match = re.search(r'Estaca\s+([\d\+\s]+(?:á|a)\s+[\d\+\s]+|[\d\+\s]+)', bloco, re.IGNORECASE)
        if estaca_match:
            e_texto = estaca_match.group(1).strip().replace('á', 'a')
            estaca = f"Estaca {e_texto}"
        else:
            estaca = "Estaca não informada"

        lado = "LD/LE não informado"
        if re.search(r'Bordo\s+Direito', bloco, re.IGNORECASE):
            lado = "LD"
        elif re.search(r'Bordo\s+Esquerdo', bloco, re.IGNORECASE):
            lado = "LE"
        elif re.search(r'L\.?D\.?\s*e\s*L\.?E\.?|LE\s*e\s*LD|LD\s*e\s*LE', bloco, re.IGNORECASE):
            lado = "LE e LD" if "LE e LD" in bloco else "LD e LE"
        elif re.search(r'\bL\.?D\.?\b', bloco, re.IGNORECASE):
            lado = "LD"
        elif re.search(r'\bL\.?E\.?\b', bloco, re.IGNORECASE):
            lado = "LE"

        atividade = bloco
        if rua_match:
            atividade = atividade.replace(rua_match.group(0), "")
        if estaca_match:
            atividade = atividade.replace(estaca_match.group(0), "")

        atividade = re.sub(r'RDO\s*\d{2}/\d{2}/\d{2,4}\.?', '', atividade, flags=re.IGNORECASE)
        atividade = re.sub(r'Lote\s*[\d\.]+', '', atividade, flags=re.IGNORECASE)
        atividade = re.sub(r'Slump\s*[\d\,\.]+cm', '', atividade, flags=re.IGNORECASE)
        atividade = re.sub(r'Bordo\s+(Direito|Esquerdo)', '', atividade, flags=re.IGNORECASE)
        atividade = re.sub(r'\bL\.?[DE]\.?\b', '', atividade, flags=re.IGNORECASE)
        atividade = re.sub(r'estaca', '', atividade, flags=re.IGNORECASE)
        atividade = re.sub(r'[\r\n\s]+', ' ', atividade).strip()
        atividade = re.sub(r'^[\-\.\:\s]+', '', atividade)

        linha = f"{rua} - {estaca} - {lado} - {atividade}"
        linhas_finais.append(linha)

    return linhas_finais

if st.button("🚀 Gerar Relatório", type="primary"):
    resultado = processar_rdo(texto_bruto)
    if resultado:
        texto_final = "\n".join(resultado)
        st.success(f"✅ Sucesso! {len(resultado)} registros formatados.")
        st.text_area("Resultado formatado (pronto para copiar):", value=texto_final, height=350)
    else:
        st.warning("Nenhum registro válido foi encontrado no texto.")
