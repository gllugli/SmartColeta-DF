<div align="center">
  <h1>🚛 SmartColeta-DF: plataforma para apoio a decisões</h1>
  <h5>Projeto feito para a disciplina Projeto Integrador I do Centro Universitário de Brasília</h5>
</div>

## ♻️ 1. Descrição do Projeto

O SmartColeta-DF é um sistema web desenvolvido para apoiar a tomada de decisões de empresas responsáveis pela coleta e descarte de resíduos sólidos no Distrito Federal, com o objetivo de colaborar na gestão das coletas, a ajudar na otimização e gestão de rotas e contribuir para a redução de custos operacionais.

A plataforma permite que gestores planejem suas rotas com base em dados coletados, utilizando informações como volume de resíduos por região, pontos de coleta, indicadores de custo, "ranking" com as regiões com a maior produção de resíduos e resumos da região por meio de filtros. Fatores que impactam diretamente a eficiência logística das operações. Seu uso é contínuo no contexto do planejamento operacional, possibilitando maior previsibilidade e melhor alocação de recursos.

Dessa forma, o sistema busca aumentar a eficiência das operações por meio do uso estratégico de dados, promovendo decisões mais assertivas e fundamentadas. Além disso, o projeto se alinha ao Objetivo de Desenvolvimento Sustentável 11 (ODS 11) – Cidades e Comunidades Sustentáveis, ao contribuir para a melhoria da gestão de resíduos urbanos, a redução de impactos ambientais e a promoção de cidades mais eficientes e sustentáveis.

## 🎯 2. Objetivos Iniciais
Para a primeira fase deste projeto, nosso foco é a pesquisa e análise de dados para validar a necessidade e nortear o desenvolvimento de uma solução completa. Os objetivos são:

📊 Coletar e Estruturar Dados: Realizar a coleta de dados de fontes confiáveis e públicas sobre coleta de resíduos sólidos. \
📈 Desenvolver um Dashboard: Criar um protótipo visual de um dashboard para visualização dos dados coletados. \
🔍 Analisar os dados: Utilizar o conceito do dashboard para identificar possíveis variáveis que colaborem com a decisão da rota para uma otimização da coleta. \
💡 Justificar a Solução: Usar a análise de dados como embasamento para definir os requisitos e as funcionalidades da plataforma "SmartColeta-DF" a ser desenvolvida nas próximas etapas do projeto integrador.

## 🖥️ 3. Dashboard dinâmico

O MVP roda como um dashboard Python dinâmico. O servidor usa a planilha tratada em `docs/Entrega_3/Base_dados_SMART_tratada.xlsx`, aplica os filtros recebidos pela URL e renderiza os indicadores e gráficos no HTML. Os dados ficam em cache em memória por instância e são recarregados quando a planilha muda.

### Arquitetura

```text
api/                            Entrada da Python Function da Vercel
smartcoleta/               Pacote da aplicação dinâmica
public/static/              CSS público do dashboard
docs/Entrega_3/         Base bruta, base tratada, ETL e dicionário de dados
docs/Entrega_*/         Entregáveis acadêmicos e materiais de apoio
tests/                           Testes automatizados mínimos do dashboard
```

O pacote `smartcoleta` concentra o código executável da aplicação. A pasta `docs` fica reservada para documentação, entregáveis e bases usadas pelo projeto.

### Execução local

Instale as dependências:

```bash
pip install -r requirements.txt
```

Para executar:

```bash
python app.py
```

Também é possível executar com:

```bash
python -m smartcoleta
```

Depois, acesse `http://127.0.0.1:8000`. Os filtros recalculam os indicadores e gráficos com base na planilha.

### Testes

Execute os testes com:

```bash
python -m unittest discover -s tests
```

## 👥 4. Membros da Equipe e Papéis

| Membro                | Papel                                      |
| --------------------- | ------------------------------------------ |
| 👑 **[Arthur de Jesus](https://github.com/BonnBonn-stack)** | **Project Owner** |
| ✒ **[Pedro Felizardo](https://github.com/pedro-felizardo)** | **Scrum Master** |
| 🗃️ **[Pedro Augusto](https://github.com/Augusto0l)** | **Arquiteto do Sistema** |
| 💻 **[João Pedro Roriz](https://github.com/JPedra121)** | **Administrador de Banco de Dados** |
| 💻 **[Gabriel Lugli](https://github.com/gllugli)** | **Desenvolvedor Full-Stack** |
