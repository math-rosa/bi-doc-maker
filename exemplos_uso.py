"""
Exemplo de uso do Documentador de Projetos Power BI

Este script demonstra diferentes formas de usar o documentador_pbip.py
"""

from documentador_pbip import DocumentadorPBIP
from pathlib import Path


def exemplo_basico():
    """Exemplo básico: documentar um único projeto"""
    print("=" * 60)
    print("EXEMPLO 1: Uso Básico")
    print("=" * 60)
    
    # Caminho para o projeto
    caminho_projeto = "C:/Caminho/Para/Projeto"
    
    # Criar documentador
    doc = DocumentadorPBIP(caminho_projeto)
    
    # Extrair informações
    doc.extrair_informacoes()
    
    # Gerar e salvar documentação
    doc.salvar_documentacao()
    
    print("\n✓ Documentação gerada!")


def exemplo_multiplos_projetos():
    """Exemplo 2: Processar múltiplos projetos"""
    print("\n" + "=" * 60)
    print("EXEMPLO 2: Múltiplos Projetos")
    print("=" * 60)
    
    projetos = [
        "C:/Projetos/Vendas",
        "C:/Projetos/Marketing",
        "C:/Projetos/Financeiro"
    ]
    
    for projeto in projetos:
        try:
            print(f"\n📊 Processando: {Path(projeto).name}")
            
            doc = DocumentadorPBIP(projeto)
            doc.extrair_informacoes()
            
            # Salvar com nome customizado
            nome_saida = f"DOC_{Path(projeto).name}.md"
            doc.salvar_documentacao(nome_saida)
            
            print(f"  ✓ Salvo como: {nome_saida}")
            
        except Exception as e:
            print(f"  ❌ Erro: {e}")


def exemplo_analise_tabelas():
    """Exemplo 3: Analisar tabelas e medidas"""
    print("\n" + "=" * 60)
    print("EXEMPLO 3: Análise de Tabelas")
    print("=" * 60)
    
    caminho_projeto = "C:/Caminho/Para/Projeto"
    
    doc = DocumentadorPBIP(caminho_projeto)
    doc.extrair_informacoes()
    
    # Estatísticas
    print(f"\n📈 Estatísticas do Projeto:")
    print(f"  • Total de tabelas: {len(doc.tabelas)}")
    print(f"  • Total de relacionamentos: {len(doc.relacionamentos)}")
    print(f"  • Total de páginas: {len(doc.paginas)}")
    
    # Tabelas com mais medidas
    print(f"\n📊 Top 5 Tabelas por Número de Medidas:")
    tabelas_ordenadas = sorted(doc.tabelas, key=lambda t: len(t.medidas), reverse=True)
    for i, tabela in enumerate(tabelas_ordenadas[:5], 1):
        print(f"  {i}. {tabela.nome}: {len(tabela.medidas)} medidas")
    
    # Medidas complexas (mais de 100 caracteres)
    print(f"\n🔍 Medidas Complexas (DAX > 100 caracteres):")
    for tabela in doc.tabelas:
        for medida in tabela.medidas:
            if len(medida.expressao_dax) > 100:
                print(f"  • {tabela.nome}.{medida.nome}")
                print(f"    {medida.expressao_dax[:80]}...")
    
    # Salvar documentação
    doc.salvar_documentacao()


def exemplo_filtrar_tabelas_fato():
    """Exemplo 4: Filtrar apenas tabelas de fato"""
    print("\n" + "=" * 60)
    print("EXEMPLO 4: Filtrar Tabelas de Fato")
    print("=" * 60)
    
    caminho_projeto = "C:/Caminho/Para/Projeto"
    
    doc = DocumentadorPBIP(caminho_projeto)
    doc.extrair_informacoes()
    
    # Filtrar tabelas de fato (convenção: começam com "Fato" ou "F_")
    tabelas_fato = [
        t for t in doc.tabelas 
        if t.nome.startswith('Fato') or t.nome.startswith('F_')
    ]
    
    print(f"\n📋 Tabelas de Fato Encontradas ({len(tabelas_fato)}):")
    for tabela in tabelas_fato:
        print(f"\n  • {tabela.nome}")
        print(f"    Colunas: {len(tabela.colunas)}")
        print(f"    Medidas: {len(tabela.medidas)}")
        
        if tabela.medidas:
            print(f"    Medidas definidas:")
            for medida in tabela.medidas[:3]:  # Primeiras 3
                print(f"      - {medida.nome}")


def exemplo_gerar_markdown_customizado():
    """Exemplo 5: Gerar Markdown customizado"""
    print("\n" + "=" * 60)
    print("EXEMPLO 5: Markdown Customizado")
    print("=" * 60)
    
    caminho_projeto = "C:/Caminho/Para/Projeto"
    
    doc = DocumentadorPBIP(caminho_projeto)
    doc.extrair_informacoes()
    
    # Gerar markdown padrão
    markdown_padrao = doc.gerar_documentacao()
    
    # Criar versão customizada apenas com resumo
    markdown_resumo = f"""# Resumo do Projeto {doc.nome_projeto}

## Visão Geral

- **Tabelas**: {len(doc.tabelas)}
- **Relacionamentos**: {len(doc.relacionamentos)}
- **Páginas**: {len(doc.paginas)}
- **Medidas Totais**: {sum(len(t.medidas) for t in doc.tabelas)}

## Lista de Tabelas

"""
    
    for tabela in doc.tabelas:
        markdown_resumo += f"### {tabela.nome}\n"
        markdown_resumo += f"- Colunas: {len(tabela.colunas)}\n"
        markdown_resumo += f"- Medidas: {len(tabela.medidas)}\n"
        markdown_resumo += f"- Status: {'Oculta' if tabela.esta_oculta else 'Visível'}\n\n"
    
    # Salvar versão resumida
    caminho_resumo = Path(doc.caminho_projeto) / f"{doc.nome_projeto}_RESUMO.md"
    with open(caminho_resumo, 'w', encoding='utf-8') as f:
        f.write(markdown_resumo)
    
    print(f"\n✓ Documentação resumida salva: {caminho_resumo}")
    
    # Salvar versão completa
    doc.salvar_documentacao()


def exemplo_validar_modelo():
    """Exemplo 6: Validar estrutura do modelo"""
    print("\n" + "=" * 60)
    print("EXEMPLO 6: Validação do Modelo")
    print("=" * 60)
    
    caminho_projeto = "C:/Caminho/Para/Projeto"
    
    doc = DocumentadorPBIP(caminho_projeto)
    doc.extrair_informacoes()
    
    print("\n🔍 Validações:")
    
    # 1. Tabelas sem relacionamentos
    tabelas_com_rel = set()
    for rel in doc.relacionamentos:
        tabelas_com_rel.add(rel.tabela_origem)
        tabelas_com_rel.add(rel.tabela_destino)
    
    tabelas_isoladas = [t.nome for t in doc.tabelas if t.nome not in tabelas_com_rel]
    
    if tabelas_isoladas:
        print(f"\n⚠ Tabelas sem relacionamentos ({len(tabelas_isoladas)}):")
        for nome in tabelas_isoladas:
            print(f"  • {nome}")
    else:
        print(f"\n✓ Todas as tabelas possuem relacionamentos")
    
    # 2. Relacionamentos bidirecionais
    rel_bidirecionais = [r for r in doc.relacionamentos if r.filtro_bidirecional]
    
    if rel_bidirecionais:
        print(f"\n⚠ Relacionamentos bidirecionais ({len(rel_bidirecionais)}):")
        for rel in rel_bidirecionais:
            print(f"  • {rel.tabela_origem} ↔ {rel.tabela_destino}")
    else:
        print(f"\n✓ Nenhum relacionamento bidirecional")
    
    # 3. Tabelas sem medidas
    tabelas_sem_medidas = [t for t in doc.tabelas if not t.medidas and 'Dim' not in t.nome]
    
    if tabelas_sem_medidas:
        print(f"\n⚠ Tabelas de fato sem medidas ({len(tabelas_sem_medidas)}):")
        for tabela in tabelas_sem_medidas:
            print(f"  • {tabela.nome}")
    
    # 4. Relacionamentos inativos
    rel_inativos = [r for r in doc.relacionamentos if not r.esta_ativo]
    
    if rel_inativos:
        print(f"\n⚠ Relacionamentos inativos ({len(rel_inativos)}):")
        for rel in rel_inativos:
            print(f"  • {rel.tabela_origem} → {rel.tabela_destino}")
    
    print(f"\n✓ Validação concluída!")


if __name__ == "__main__":
    print("""
╔══════════════════════════════════════════════════════════╗
║  EXEMPLOS DE USO - Documentador Power BI                ║
╚══════════════════════════════════════════════════════════╝

Escolha um exemplo para executar:

1. Uso Básico
2. Múltiplos Projetos
3. Análise de Tabelas
4. Filtrar Tabelas de Fato
5. Markdown Customizado
6. Validar Modelo

0. Sair
""")
    
    try:
        escolha = input("Escolha (0-6): ").strip()
        
        if escolha == "1":
            exemplo_basico()
        elif escolha == "2":
            exemplo_multiplos_projetos()
        elif escolha == "3":
            exemplo_analise_tabelas()
        elif escolha == "4":
            exemplo_filtrar_tabelas_fato()
        elif escolha == "5":
            exemplo_gerar_markdown_customizado()
        elif escolha == "6":
            exemplo_validar_modelo()
        elif escolha == "0":
            print("Saindo...")
        else:
            print("Opção inválida!")
    
    except Exception as e:
        print(f"\n❌ Erro ao executar exemplo: {e}")
        import traceback
        traceback.print_exc()
