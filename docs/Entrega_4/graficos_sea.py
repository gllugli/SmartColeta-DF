import pandas as pd
import seaborn as sns
import matplotlib.pyplot as plt

# =============================================================================
# CONFIGURAÇÕES DE DESIGN
# =============================================================================
sns.set_style('whitegrid')
sns.set_palette('magma') 

file_path = 'Base_dados_SMART_tratada.xlsx'
df_mensal = pd.read_excel(file_path, sheet_name='base_mensal_consolidada')
df_equip = pd.read_excel(file_path, sheet_name='equipamentos_por_ra')
df_custos = pd.read_excel(file_path, sheet_name='custos_operacao_pev')
df_pop = pd.read_excel(file_path, sheet_name='populacao_df')

fig, axes = plt.subplots(3, 2, figsize=(20, 24))
fig.suptitle('Análise Estratégica de Resíduos Sólidos - DF', fontsize=22, fontweight='bold', y=0.98)

# =============================================================================
# GRÁFICO 1: Sazonalidade da Coleta Domiciliar (Lineplot)
# =============================================================================
ax1 = axes[0, 0]
df_domiciliar = df_mensal[df_mensal['indicador'] == 'Coleta Domiciliar (t)'].copy()
df_dom_agg = df_domiciliar.groupby(['data_referencia', 'categoria'])['valor'].sum().reset_index()

sns.lineplot(data=df_dom_agg, x='data_referencia', y='valor', hue='categoria', 
             marker='o', linewidth=2.5, ax=ax1, palette='viridis')

ax1.set_title('Sazonalidade e Picos da Coleta Domiciliar (2023-2025)', fontsize=16, fontweight='bold')
ax1.set_xlabel('Mês/Ano', fontsize=12)
ax1.set_ylabel('Volume (Toneladas)', fontsize=12)
ax1.set_ylim(bottom=0)
sns.despine(ax=ax1)

# =============================================================================
# GRÁFICO 2: Distribuição de Equipamentos por RA (Heatmap)
# =============================================================================
ax2 = axes[0, 1]
top_ras = df_equip['regiao_administrativa'].value_counts().head(15).index
df_equip_top = df_equip[df_equip['regiao_administrativa'].isin(top_ras)]
equip_matrix = pd.crosstab(df_equip_top['regiao_administrativa'], df_equip_top['tipo_equipamento'])

sns.heatmap(equip_matrix, cmap='YlOrRd', annot=True, fmt='d', linewidths=.5, ax=ax2, cbar=False)

ax2.set_title('Concentração Estratégica de Equipamentos por RA', fontsize=16, fontweight='bold')
ax2.set_xlabel('Tipo de Equipamento', fontsize=12)
ax2.set_ylabel('Região Administrativa', fontsize=12)

# =============================================================================
# GRÁFICO 3: Impacto Domiciliar vs Entulho Mecanizado (KDE Plot / Densidade)
# =============================================================================
ax3 = axes[1, 0]
df_impacto = df_mensal[df_mensal['indicador'].isin(['Coleta Domiciliar (t)', 'Entulho Mecanizado (t)'])]

sns.kdeplot(data=df_impacto, x='valor', hue='indicador', fill=True, 
            common_norm=False, palette='mako', alpha=0.6, linewidth=0, ax=ax3)

ax3.set_title('Distribuição de Volume: Lixo Domiciliar vs Entulho Mecanizado', fontsize=16, fontweight='bold')
ax3.set_xlabel('Volume Mensal Coletado (Toneladas)', fontsize=12)
ax3.set_ylabel('Densidade de Frequência', fontsize=12)
sns.despine(ax=ax3)

# =============================================================================
# GRÁFICO 4: Correlação Demográfica vs Infraestrutura (Bubble Scatter Plot)
# =============================================================================
ax4 = axes[1, 1]
df_pop_24 = df_pop[df_pop['ano'] == 2024].groupby('regiao_administrativa')['pop_total'].sum().reset_index()
df_equip_count = df_equip.groupby('regiao_administrativa').size().reset_index(name='qtd_equipamentos')
df_corr = pd.merge(df_pop_24, df_equip_count, on='regiao_administrativa', how='inner')

sns.scatterplot(data=df_corr, x='pop_total', y='qtd_equipamentos', size='pop_total', 
                sizes=(50, 1000), alpha=0.7, color='indigo', ax=ax4, legend=False)

ax4.set_xlim(left=0) 
ax4.set_ylim(bottom=0) 
ax4.margins(x=0.15, y=0.15)

# Seleção das RAs extremas para destaque
top_pop = df_corr.nlargest(4, 'pop_total')
top_equip = df_corr.nlargest(4, 'qtd_equipamentos')
pontos_destaque = pd.concat([top_pop, top_equip]).drop_duplicates()

offset_x = df_corr['pop_total'].max() * 0.022 

# --- AJUSTE CONDICIONAL FINAL DE POSIÇÃO E NOME DOS TEXTOS ---
for idx, row in pontos_destaque.iterrows():
    ra_nome = row['regiao_administrativa']
    
    # Define o nome que aparecerá no gráfico
    nome_exibicao = ra_nome 
    
    # Configurações padrão (para a maioria das RAs)
    x_pos = row['pop_total'] + offset_x
    y_pos = row['qtd_equipamentos']
    alinhamento_h = 'left'
    alinhamento_v = 'center'
    
    # Customização individual para evitar colisões específicas
    if ra_nome == 'Sudoeste/Octogonal':
        nome_exibicao = 'Sudoeste'           # Ajuste: Encurta o nome para não cortar o eixo
        x_pos = row['pop_total'] - offset_x
        y_pos = row['qtd_equipamentos'] + 2.5  
        alinhamento_h = 'right'
        alinhamento_v = 'bottom'             
    elif ra_nome == 'Taguatinga':
        x_pos = row['pop_total'] - offset_x
        alinhamento_h = 'right'

    ax4.text(x_pos, y_pos, 
             nome_exibicao, fontsize=10, ha=alinhamento_h, va=alinhamento_v, # Agora usa a variável nome_exibicao
             bbox=dict(facecolor='white', alpha=0.7, edgecolor='none', pad=1.5))

ax4.set_title('População vs Disponibilidade de Infraestrutura Física', fontsize=16, fontweight='bold')
ax4.set_xlabel('População Total da RA', fontsize=12)
ax4.set_ylabel('Quantidade de Equipamentos', fontsize=12)
sns.despine(ax=ax4)

# =============================================================================
# GRÁFICO 5: Estabilidade vs Variação nos Custos PEV (Stripplot + Pointplot)
# =============================================================================
ax5 = axes[2, 0]
df_custos_filtered = df_custos[df_custos['categoria'] != 'Custo total']

sns.stripplot(data=df_custos_filtered, x='valor', y='categoria', hue='categoria', 
              jitter=True, size=8, alpha=0.6, ax=ax5, legend=False)
sns.pointplot(data=df_custos_filtered, x='valor', y='categoria', color='black', 
              markers="x", linestyles="", ax=ax5)

ax5.set_xlim(left=0)
ax5.set_title('Variação e Ancoragem dos Custos Mensais de PEV', fontsize=16, fontweight='bold')
ax5.set_xlabel('Custo Operacional Mensal (R$)', fontsize=12)
ax5.set_ylabel('')
sns.despine(ax=ax5)

fig.delaxes(axes[2, 1])

plt.tight_layout(pad=4.0, h_pad=4.0, w_pad=3.0) 
plt.show()
