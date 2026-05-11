# ============================================================
# ETL - Base de dados SMART Coleta
# Projeto Integrador I - SmartColeta-DF
# ============================================================
# Neste script fazemos a limpeza da planilha original do projeto.
# A ideia é manter a base bruta preservada e gerar um novo arquivo
# com os dados mais organizados para análise.
# ============================================================

from pathlib import Path
import re
import unicodedata
import pandas as pd

# ------------------------------------------------------------
# 1. Configurações iniciais
# ------------------------------------------------------------
# Deixamos mais de uma opção de nome para o arquivo de entrada,
# porque durante os ajustes a planilha foi salva com nomes diferentes.
ARQUIVOS_ENTRADA_POSSIVEIS = [
    Path("Base_dados_SMART_corrigida.xlsx"),
    Path("Base_dados_SMART(1).xlsx"),
    Path("Base_dados_SMART.xlsx"),
]
ARQUIVO_SAIDA = Path("Base_dados_SMART_tratada.xlsx")

MESES = {
    "JAN": "01", "JANEIRO": "01",
    "FEV": "02", "FEVEREIRO": "02",
    "MAR": "03", "MARCO": "03", "MARÇO": "03",
    "ABR": "04", "ABRIL": "04",
    "MAI": "05", "MAIO": "05",
    "JUN": "06", "JUNHO": "06",
    "JUL": "07", "JULHO": "07",
    "AGO": "08", "AGOSTO": "08",
    "SET": "09", "SETEMBRO": "09",
    "OUT": "10", "OUTUBRO": "10",
    "NOV": "11", "NOVEMBRO": "11",
    "DEZ": "12", "DEZEMBRO": "12",
}

ABAS_TEXTO = {"Papa_Entulho_P60", "Papa_Lixo", "Papa_Reciclavel_P66"}
ABAS_CUSTOS_LOTES = {"Custos_Lotes_I", "Custos_Lotes_II", "Custos_Lotes_III", "Custos_Lotes_TOTAL"}

# ------------------------------------------------------------
# Filtros combinados pelo grupo
# ------------------------------------------------------------
# Depois de revisar a planilha tratada, decidimos retirar alguns
# indicadores que não fariam parte do recorte usado no projeto.
INDICADORES_REMOVER = {
    "Catação (eqp)",
    "Composto Doado (t)",
    "Processamento Usinas (t)",
    "Produção Composto (t)",
    "Transbordo Resíduos (t)",
    "Varrição Manual (km)",
    "Varrição Mecanizada (km)",
}

CATEGORIAS_CUSTOS_LOTES_REMOVER = {
    "Lavagem de Vias e Logradouros públicos",
    "Limpeza Pós- eventos e Coleta de Resíduos de Caixa de Gordura",
    "Limpeza Pós Eventos e Coleta de Resíduos de Caixa de Gordura",
    "Limpeza de equipamentos e Bens Públicos",
    "Pintura Mecanizada de Meio-Fio e Frisagem",
    "Unidade de Transbordo de Rejeitos e/ou Resíduos - Asa Sul e Sobradinho",
    "Unidade de Transbordo de Rejeitos e/ou Resíduos",
    "Varrição manual de vias",
    "Varrição mecanizada de vias",
}

CATEGORIAS_CUSTOS_URE_ASB_REMOVER = {
    "CUSTOS INDIRETOS, LUCROS E TRIBUTOS- BDI 20,45%",
}

# Também criamos uma versão simplificada dos textos para comparar
# os nomes mesmo quando houver acento, quebra de linha ou espaços a mais.
def normalizar_texto_para_comparacao(valor):
    if valor is None or pd.isna(valor):
        return ""
    txt = str(valor).strip().lower()
    txt = unicodedata.normalize("NFKD", txt)
    txt = "".join(ch for ch in txt if not unicodedata.combining(ch))
    txt = re.sub(r"\s+", " ", txt)
    return txt

INDICADORES_REMOVER_NORM = {normalizar_texto_para_comparacao(v) for v in INDICADORES_REMOVER}
CATEGORIAS_CUSTOS_LOTES_REMOVER_NORM = {normalizar_texto_para_comparacao(v) for v in CATEGORIAS_CUSTOS_LOTES_REMOVER}
CATEGORIAS_CUSTOS_URE_ASB_REMOVER_NORM = {normalizar_texto_para_comparacao(v) for v in CATEGORIAS_CUSTOS_URE_ASB_REMOVER}

# ------------------------------------------------------------
# 2. Funções auxiliares de limpeza
# ------------------------------------------------------------
def localizar_arquivo_entrada():
    """Procura a planilha de entrada na mesma pasta do script."""
    for caminho in ARQUIVOS_ENTRADA_POSSIVEIS:
        if caminho.exists():
            return caminho

    candidatos = sorted(Path(".").glob("Base_dados_SMART*.xlsx"))
    candidatos = [c for c in candidatos if "tratada" not in c.name.lower()]
    if candidatos:
        return candidatos[0]

    raise FileNotFoundError(
        "Nenhuma base de entrada foi encontrada. Coloque a planilha suja na mesma pasta do script."
    )


def texto_limpo(valor):
    """Limpa textos simples, retirando espaços e quebras de linha desnecessárias."""
    if pd.isna(valor):
        return None
    valor = str(valor).replace("\n", " ").strip()
    valor = re.sub(r"\s+", " ", valor)
    return valor if valor else None


def normalizar_mes(valor):
    """Transforma o nome do mês no número correspondente."""
    valor = texto_limpo(valor)
    if not valor:
        return None
    chave = valor.upper().replace(".", "")
    chave = re.sub(r"[^A-ZÁÉÍÓÚÂÊÔÃÕÇ]", "", chave)
    return MESES.get(chave)


def numero_brasileiro_para_float(valor):
    """Converte valores monetários ou numéricos para o formato usado pelo Python.

    Exemplos:
    '22.557,55' vira 22557.55
    'R$ 1.360,00' vira 1360.00
    '-' vira 0.0 quando aparece em campo numérico.
    """
    if pd.isna(valor):
        return None
    valor = str(valor).strip()
    if valor in {"", "-", "–", "—"}:
        return 0.0
    valor = valor.replace("R$", "").replace(" ", "")
    valor = valor.replace(".", "").replace(",", ".")
    valor = re.sub(r"[^0-9.\-]", "", valor)
    if valor in {"", ".", "-"}:
        return None
    try:
        return float(valor)
    except ValueError:
        return None


def remover_linhas_colunas_vazias(df):
    """Retira linhas e colunas que não têm nenhuma informação."""
    df = df.dropna(axis=0, how="all").dropna(axis=1, how="all")
    df = df.reset_index(drop=True)
    df.columns = range(df.shape[1])
    return df


def primeiro_texto(row, colunas):
    """Busca o primeiro texto válido entre algumas colunas da linha."""
    for col in colunas:
        if col in row.index:
            val = texto_limpo(row[col])
            if val and not re.fullmatch(r"20\d{2}", val):
                return val
    return None


def ano_da_linha(row):
    """Procura um ano na linha analisada."""
    for val in row.tolist():
        txt = texto_limpo(val)
        if txt and re.fullmatch(r"20\d{2}", txt):
            return int(txt)
    return None


def linha_tem_valor_numerico(row, colunas_valor):
    """Confere se a linha tem algum valor numérico nas colunas dos meses."""
    for col in colunas_valor:
        if col in row.index and numero_brasileiro_para_float(row[col]) is not None:
            return True
    return False


def deve_remover_por_termos(valor, termos_norm):
    """Verifica se o texto contém algum termo que deve ser removido."""
    valor_norm = normalizar_texto_para_comparacao(valor)
    if not valor_norm:
        return False
    return any(termo and termo in valor_norm for termo in termos_norm)

# ------------------------------------------------------------
# 3. Organização das tabelas mensais
# ------------------------------------------------------------
def extrair_blocos_mensais(nome_aba, df):
    """Lê as tabelas em que os meses aparecem como colunas e reorganiza os dados.

    A planilha original veio com várias estruturas diferentes. Em muitas
    abas, os meses ficam espalhados em colunas e existem blocos de dados
    dentro da mesma aba. Aqui localizamos esses blocos e transformamos
    cada valor mensal em uma linha separada.
    """
    df = remover_linhas_colunas_vazias(df)
    registros = []
    i = 0
    indicador_atual = None

    while i < len(df):
        row = df.iloc[i]
        meses_cols = {col: normalizar_mes(row[col]) for col in df.columns}
        meses_cols = {col: mes for col, mes in meses_cols.items() if mes}

        # Nesta aba os meses não aparecem claramente no cabeçalho, então usamos a posição das colunas.
        if nome_aba == "Remocao_PEV_P64" and i == 0:
            colunas_mensais = [c for c in df.columns if c >= 2 and c % 3 == 2][:12]
            meses_cols = {col: str(idx + 1).zfill(2) for idx, col in enumerate(colunas_mensais)}
            indicador_atual = "Remoção PEV (t)"

        if len(meses_cols) >= 2:
            primeira_col_mes = min(meses_cols.keys())
            possiveis_indicadores = [c for c in df.columns if c < primeira_col_mes]
            cabecalho = primeiro_texto(row, possiveis_indicadores)
            if cabecalho and cabecalho.upper() not in {"MÊS", "MES", "UNIDADE", "TOTAL_REMOCAO_PEV(T)"}:
                indicador_atual = cabecalho

            j = i + 1 if nome_aba != "Remocao_PEV_P64" else i
            while j < len(df):
                prox = df.iloc[j]
                prox_meses = {col: normalizar_mes(prox[col]) for col in df.columns}
                prox_meses = {col: mes for col, mes in prox_meses.items() if mes}
                if j != i and len(prox_meses) >= 2:
                    break

                if linha_tem_valor_numerico(prox, list(meses_cols.keys())):
                    ano = ano_da_linha(prox) or ano_da_linha(row)
                    categoria = primeiro_texto(prox, [c for c in df.columns if c < primeira_col_mes])

                    # Em alguns pontos o nome da categoria ficou quebrado em mais de uma linha.
                    # Quando isso acontece, juntamos o complemento ao nome principal.
                    complemento = []
                    k = j + 1
                    while k < len(df):
                        futura = df.iloc[k]
                        futura_meses = {col: normalizar_mes(futura[col]) for col in df.columns}
                        futura_meses = {col: mes for col, mes in futura_meses.items() if mes}
                        if len(futura_meses) >= 2 or linha_tem_valor_numerico(futura, list(meses_cols.keys())):
                            break
                        txt = primeiro_texto(futura, [c for c in df.columns if c < primeira_col_mes])
                        if txt:
                            complemento.append(txt)
                        k += 1
                    if complemento and categoria:
                        categoria = " ".join([categoria] + complemento)

                    for col, mes in meses_cols.items():
                        valor = numero_brasileiro_para_float(prox[col])
                        if valor is not None:
                            registros.append({
                                "aba_origem": nome_aba,
                                "ano": ano,
                                "mes": mes,
                                "data_referencia": f"{ano}-{mes}-01" if ano else None,
                                "indicador": texto_limpo(indicador_atual) or "Indicador não identificado",
                                "categoria": texto_limpo(categoria),
                                "valor": valor,
                            })
                j += 1

            i = j
        else:
            # Guarda o último título encontrado para usar como indicador das próximas linhas.
            textos = [texto_limpo(v) for v in row.tolist() if texto_limpo(v)]
            if textos and len(textos) <= 2:
                indicador_atual = textos[-1]
            i += 1

    return pd.DataFrame(registros)

# ------------------------------------------------------------
# 4. Tratamentos de abas específicas
# ------------------------------------------------------------
def tratar_populacao(df):
    """Organiza a aba com os dados de população do DF."""
    df = remover_linhas_colunas_vazias(df)
    df.columns = ["ano", "regiao_administrativa", "mulheres", "homens", "pop_total"] + [f"extra_{i}" for i in range(df.shape[1] - 5)]
    df = df[["ano", "regiao_administrativa", "mulheres", "homens", "pop_total"]]
    df = df.dropna(how="all")
    df = df[df["regiao_administrativa"].notna()]
    df["regiao_administrativa"] = df["regiao_administrativa"].astype(str).str.replace("⊕", "", regex=False).str.strip()
    df = df[df["regiao_administrativa"].str.lower() != "região administrativa"]
    for col in ["ano", "mulheres", "homens", "pop_total"]:
        df[col] = pd.to_numeric(df[col], errors="coerce")
    df = df.drop_duplicates()
    return df


def extrair_textos(nome_aba, df):
    """Mantém o conteúdo das abas que têm mais texto do que tabela numérica."""
    df = remover_linhas_colunas_vazias(df)
    linhas = []
    for _, row in df.iterrows():
        textos = [texto_limpo(v) for v in row.tolist() if texto_limpo(v)]
        if textos:
            linhas.append(" ".join(textos))
    texto = "\n".join(linhas)
    return pd.DataFrame([{"aba_origem": nome_aba, "conteudo_textual": texto}])


def encontrar_linha_cabecalho_vertical(df, linha_dado):
    """Procura o cabeçalho mais próximo acima da linha que está sendo lida."""
    for r in range(linha_dado - 1, -1, -1):
        textos = [normalizar_texto_para_comparacao(v) for v in df.iloc[r].tolist() if texto_limpo(v)]
        if any(t in {"mes", "mês"} for t in textos):
            return r
    return max(0, linha_dado - 4)


def construir_categoria_vertical(df, linha_dado, col_valor, secao_atual):
    """Monta o nome da categoria nas tabelas em que os meses ficam nas linhas.

    Nessa aba, os cabeçalhos não ficaram em uma única linha. Por isso,
    juntamos as partes do cabeçalho para chegar ao nome da categoria.
    Quando a coluna exata está vazia, olhamos as colunas vizinhas.
    """
    linha_cabecalho = encontrar_linha_cabecalho_vertical(df, linha_dado)

    def coletar_partes(colunas_busca):
        partes = []
        for r in range(linha_cabecalho, linha_dado):
            if any(normalizar_mes(df.iat[r, c]) for c in df.columns):
                break
            for c in colunas_busca:
                if c in df.columns:
                    txt = texto_limpo(df.iat[r, c])
                    if not txt:
                        continue
                    txt_norm = normalizar_texto_para_comparacao(txt)
                    if txt_norm in {"mes", "mês"}:
                        continue
                    if normalizar_mes(txt):
                        continue
                    if secao_atual and normalizar_texto_para_comparacao(txt) == normalizar_texto_para_comparacao(secao_atual):
                        continue
                    if re.fullmatch(r"20\d{2}", txt):
                        continue
                    partes.append(txt)
        unicas = []
        for p in partes:
            if p not in unicas:
                unicas.append(p)
        return unicas

    partes = coletar_partes([col_valor])
    if not partes:
        partes = coletar_partes([col_valor - 1])
    if not partes:
        partes = coletar_partes([col_valor + 1])

    categoria = " ".join(partes).strip()
    return categoria or f"Valor coluna {col_valor}"

def extrair_custos_operacao_pev(nome_aba, df):
    """Trata a aba Custo_Operacao_PEV_P79 separadamente.

    Diferente das outras abas, aqui os meses aparecem nas linhas e os custos
    aparecem nas colunas. Por isso, usamos uma lógica própria para deixar
    esses dados no mesmo padrão das demais bases.
    """
    df = remover_linhas_colunas_vazias(df)
    registros = []
    secao_atual = None

    for i, row in df.iterrows():
        textos = [texto_limpo(v) for v in row.tolist() if texto_limpo(v)]
        mes_col = None
        mes_num = None

        for col in df.columns:
            mes = normalizar_mes(row[col])
            if mes:
                mes_col = col
                mes_num = mes
                break

        if mes_col is not None:
            ano = ano_da_linha(row)
            if not ano:
                # Em algumas seções o ano está no cabeçalho, então procuramos nas linhas anteriores.
                for r in range(i, max(-1, i - 6), -1):
                    ano = ano_da_linha(df.iloc[r])
                    if ano:
                        break

            for col in df.columns:
                if col <= mes_col:
                    continue
                valor = numero_brasileiro_para_float(row[col])
                if valor is None:
                    continue

                categoria = construir_categoria_vertical(df, i, col, secao_atual)
                if normalizar_texto_para_comparacao(categoria) in {"", "mes"}:
                    continue

                registros.append({
                    "aba_origem": nome_aba,
                    "ano": ano,
                    "mes": mes_num,
                    "data_referencia": f"{ano}-{mes_num}-01" if ano else None,
                    "secao": secao_atual or "Seção não identificada",
                    "categoria": categoria,
                    "valor": valor,
                })
        else:
            # Atualiza o nome da seção quando encontramos um título realmente útil.
            # Cabeçalhos genéricos, como "Mês", "Total" ou "Custo por tonelada", são ignorados.
            candidatos = []
            for txt in textos:
                txt_norm = normalizar_texto_para_comparacao(txt)
                if txt_norm in {"mes", "mês", "total", "custo por tonelada", "custo total"}:
                    continue
                if re.fullmatch(r"20\d{2}", txt):
                    continue
                eh_titulo = (
                    len(textos) <= 3
                    and (
                        len(txt) >= 25
                        or "custo da operacao" in txt_norm
                        or "custo da operação" in txt_norm
                        or "aterro sanitario" in txt_norm
                        or "aterro sanitário" in txt_norm
                        or "utmb" in txt_norm
                    )
                )
                if eh_titulo:
                    candidatos.append(txt)
            if candidatos:
                secao_atual = max(candidatos, key=len)

    base = pd.DataFrame(registros)
    if not base.empty:
        base["data_referencia"] = pd.to_datetime(base["data_referencia"], errors="coerce")
        base = base.drop_duplicates().sort_values(["secao", "categoria", "data_referencia"])
    return base

# ------------------------------------------------------------
# 5. Aplicação dos filtros finais
# ------------------------------------------------------------
def aplicar_filtros_feedback(base_mensal):
    """Remove da base final os itens que ficaram fora do recorte do grupo."""
    if base_mensal.empty:
        return base_mensal

    base = base_mensal.copy()

    # 1) Retira indicadores que não serão usados na análise.
    base = base[~base["indicador"].apply(lambda x: deve_remover_por_termos(x, INDICADORES_REMOVER_NORM))]

    # 2) Retira categorias específicas das abas de custos dos lotes.
    filtro_custos_lotes = (
        base["aba_origem"].isin(ABAS_CUSTOS_LOTES)
        & base["categoria"].apply(lambda x: deve_remover_por_termos(x, CATEGORIAS_CUSTOS_LOTES_REMOVER_NORM))
    )
    base = base[~filtro_custos_lotes]

    # 3) Retira a linha de BDI da aba Custos_URE_ASB_P78, quando ela aparece.
    filtro_ure_asb = (
        (base["aba_origem"] == "Custos_URE_ASB_P78")
        & base["categoria"].apply(lambda x: deve_remover_por_termos(x, CATEGORIAS_CUSTOS_URE_ASB_REMOVER_NORM))
    )
    base = base[~filtro_ure_asb]

    return base.reset_index(drop=True)

# ------------------------------------------------------------
# 6. Execução do processo
# ------------------------------------------------------------
def executar_etl():
    arquivo_entrada = localizar_arquivo_entrada()
    xls = pd.ExcelFile(arquivo_entrada)

    bases_mensais = []
    bases_textuais = []
    custos_operacao_pev = pd.DataFrame()
    populacao = pd.DataFrame()
    resumo = []

    for nome_aba in xls.sheet_names:
        df_original = pd.read_excel(arquivo_entrada, sheet_name=nome_aba, header=None, dtype=object)
        linhas_ini, colunas_ini = df_original.shape

        if nome_aba == "popul_DF":
            tratado = tratar_populacao(df_original)
            populacao = tratado
            tipo = "populacao"
        elif nome_aba == "Custo_Operacao_PEV_P79":
            tratado = extrair_custos_operacao_pev(nome_aba, df_original)
            custos_operacao_pev = tratado
            tipo = "custo_operacao_pev"
        elif nome_aba in ABAS_TEXTO:
            tratado = extrair_textos(nome_aba, df_original)
            bases_textuais.append(tratado)
            tipo = "texto"
        else:
            tratado = extrair_blocos_mensais(nome_aba, df_original)
            if not tratado.empty:
                bases_mensais.append(tratado)
            tipo = "mensal"

        resumo.append({
            "aba_origem": nome_aba,
            "tipo_tratamento": tipo,
            "linhas_originais": linhas_ini,
            "colunas_originais": colunas_ini,
            "linhas_tratadas": len(tratado),
            "colunas_tratadas": tratado.shape[1] if not tratado.empty else 0,
        })

    base_mensal = pd.concat(bases_mensais, ignore_index=True) if bases_mensais else pd.DataFrame()
    base_textual = pd.concat(bases_textuais, ignore_index=True) if bases_textuais else pd.DataFrame()
    resumo_qualidade = pd.DataFrame(resumo)

    # Última conferência da base mensal antes de salvar o arquivo final.
    if not base_mensal.empty:
        base_mensal["indicador"] = base_mensal["indicador"].apply(texto_limpo)
        base_mensal["categoria"] = base_mensal["categoria"].apply(texto_limpo)
        base_mensal["valor"] = pd.to_numeric(base_mensal["valor"], errors="coerce")
        base_mensal["data_referencia"] = pd.to_datetime(base_mensal["data_referencia"], errors="coerce")
        base_mensal = base_mensal.drop_duplicates()
        base_mensal = aplicar_filtros_feedback(base_mensal)
        base_mensal = base_mensal.sort_values(["aba_origem", "indicador", "categoria", "data_referencia"])

    # Geração da planilha tratada.
    with pd.ExcelWriter(ARQUIVO_SAIDA, engine="openpyxl") as writer:
        base_mensal.to_excel(writer, sheet_name="base_mensal_consolidada", index=False)
        populacao.to_excel(writer, sheet_name="populacao_df", index=False)
        custos_operacao_pev.to_excel(writer, sheet_name="custos_operacao_pev", index=False)
        base_textual.to_excel(writer, sheet_name="textos_extraidos", index=False)
        resumo_qualidade.to_excel(writer, sheet_name="resumo_qualidade", index=False)

    print("ETL concluído com sucesso.")
    print(f"Arquivo de entrada: {arquivo_entrada}")
    print(f"Arquivo gerado: {ARQUIVO_SAIDA}")
    print(f"Registros mensais tratados: {len(base_mensal)}")
    print(f"Registros de custos de operação PEV/ASB tratados: {len(custos_operacao_pev)}")
    print(f"Registros de população tratados: {len(populacao)}")


if __name__ == "__main__":
    executar_etl()
