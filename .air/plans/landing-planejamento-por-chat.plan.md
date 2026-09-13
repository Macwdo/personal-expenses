## 1. Goal

Reposicionar a landing como uma apresentação simples e convincente de planejamento financeiro acessível por IA, mostrando com exemplos fiéis como o Pingou o que? planeja, consulta e executa ações pelo chat, e converter o visitante em uma inscrição real na lista de acesso.

## 2. Approach

A narrativa seguirá um arco AIDA/StoryBrand: abrir com o contraste entre apenas enxergar o passado e decidir o próximo passo, provar a proposta com uma demonstração curta do chat e então explicar o motor financeiro real do produto. A página continuará majoritariamente composta por Server Components; somente a demonstração com troca de cenários e o formulário serão Client Components, reduzindo JavaScript e mantendo a implementação simples. A copy terá voz jovem e direta, mas sem gírias que excluam adultos, não citará concorrentes e não inventará métricas ou depoimentos.

A fonte de verdade será o produto existente: os três especialistas e suas operações estão registrados em [subagents.py](air-file://60jn4j480ks6od3snjei/home/macwdo/Codes/pingou-o-que/pingou-o-que-backend/apps/ai/subagents.py?type=file&linesData=%7B%22range%22%3A%7B%22first%22%3A409%2C%22second%22%3A1765%7D%2C%22lines%22%3A%7B%22first%22%3A15%2C%22second%22%3A46%7D%7D&root=%252F) e [tool_registry.py](air-file://60jn4j480ks6od3snjei/home/macwdo/Codes/pingou-o-que/pingou-o-que-backend/apps/ai/tool_registry.py?type=file&linesData=%7B%22range%22%3A%7B%22first%22%3A1150%2C%22second%22%3A2884%7D%2C%22lines%22%3A%7B%22first%22%3A46%2C%22second%22%3A113%7D%7D&root=%252F); as regras de recorrência, parcelas, receitas e conciliação estão documentadas em [business-rules.md](air-file://60jn4j480ks6od3snjei/home/macwdo/Codes/pingou-o-que/pingou-o-que-backend/docs/business-rules.md?type=file&linesData=%7B%22range%22%3A%7B%22first%22%3A109%2C%22second%22%3A4279%7D%2C%22lines%22%3A%7B%22first%22%3A4%2C%22second%22%3A63%7D%7D&root=%252F); e a comparação planejado × realizado já aparece na interface autenticada em [dashboard-overview.tsx](air-file://60jn4j480ks6od3snjei/home/macwdo/Codes/pingou-o-que/pingou-o-que-frontend/components/dashboard-overview.tsx?type=file&linesData=%7B%22range%22%3A%7B%22first%22%3A419%2C%22second%22%3A4835%7D%2C%22lines%22%3A%7B%22first%22%3A14%2C%22second%22%3A137%7D%7D&root=%252F).

## 3. File Changes

### Landing page

- **Modify** [page.tsx](air-file://60jn4j480ks6od3snjei/home/macwdo/Codes/pingou-o-que/pingou-o-que-landing-page/app/page.tsx?type=file&linesData=%7B%22range%22%3A%7B%22first%22%3A645%2C%22second%22%3A11875%7D%2C%22lines%22%3A%7B%22first%22%3A19%2C%22second%22%3A277%7D%7D&root=%252F): substituir as seções inline atuais por uma composição curta de hero, proposta, demonstração, capacidades reais, planos, FAQ e rodapé.
- **Modify** [hero.tsx](air-file://60jn4j480ks6od3snjei/home/macwdo/Codes/pingou-o-que/pingou-o-que-landing-page/components/hero.tsx?type=file&linesData=%7B%22range%22%3A%7B%22first%22%3A454%2C%22second%22%3A4468%7D%2C%22lines%22%3A%7B%22first%22%3A14%2C%22second%22%3A117%7D%7D&root=%252F): criar o novo hook principal, CTA para a lista e uma prévia compacta do fluxo “você pede → o agente organiza → você confirma”.
- **Create** `pingou-o-que-landing-page/components/product-sections.tsx`: Server Component com o contraste visibilidade/planejamento, o fluxo em três passos e cartões das capacidades confirmadas.
- **Create** `pingou-o-que-landing-page/components/chat-product-demo.tsx`: Client Component com `useState` local e três cenários acessíveis — planejar o mês, alterar com confirmação e conciliar uma movimentação — apresentados explicitamente como demonstração.
- **Modify** [landing-content.ts](air-file://60jn4j480ks6od3snjei/home/macwdo/Codes/pingou-o-que/pingou-o-que-landing-page/lib/landing-content.ts?type=file&linesData=%7B%22range%22%3A%7B%22first%22%3A189%2C%22second%22%3A4444%7D%2C%22lines%22%3A%7B%22first%22%3A13%2C%22second%22%3A160%7D%7D&root=%252F): centralizar copy, cenários, capacidades, planos e FAQ em português correto; preservar os preços R$ 19,99/R$ 49,99 e WhatsApp conforme confirmado.
- **Modify** [header-2.tsx](air-file://60jn4j480ks6od3snjei/home/macwdo/Codes/pingou-o-que/pingou-o-que-landing-page/components/ui/header-2.tsx?type=file&linesData=%7B%22range%22%3A%7B%22first%22%3A376%2C%22second%22%3A4435%7D%2C%22lines%22%3A%7B%22first%22%3A12%2C%22second%22%3A159%7D%7D&root=%252F): alinhar navegação desktop/mobile às novas âncoras, manter tema e CTA de lista, e fechar o menu ao navegar.
- **Modify** [pricing-section.tsx](air-file://60jn4j480ks6od3snjei/home/macwdo/Codes/pingou-o-que/pingou-o-que-landing-page/components/pricing-section.tsx?type=file&linesData=%7B%22range%22%3A%7B%22first%22%3A397%2C%22second%22%3A5009%7D%2C%22lines%22%3A%7B%22first%22%3A13%2C%22second%22%3A157%7D%7D&root=%252F): explicar os planos pelo nível de acompanhamento, manter a oferta confirmada e remover expressões de prova social não verificadas como “mais escolhido”.
- **Modify** [faqs-section.tsx](air-file://60jn4j480ks6od3snjei/home/macwdo/Codes/pingou-o-que/pingou-o-que-landing-page/components/faqs-section.tsx?type=file&linesData=%7B%22range%22%3A%7B%22first%22%3A360%2C%22second%22%3A4684%7D%2C%22lines%22%3A%7B%22first%22%3A13%2C%22second%22%3A119%7D%7D&root=%252F): consumir as perguntas centralizadas e responder objeções sobre simplicidade, IA, confirmação, importação, segurança e planos.
- **Modify** [footer.tsx](air-file://60jn4j480ks6od3snjei/home/macwdo/Codes/pingou-o-que/pingou-o-que-landing-page/components/footer.tsx?type=file&root=%252F): atualizar promessa resumida, links e CTA final conforme as novas seções.
- **Modify** [layout.tsx](air-file://60jn4j480ks6od3snjei/home/macwdo/Codes/pingou-o-que/pingou-o-que-landing-page/app/layout.tsx?type=file&linesData=%7B%22range%22%3A%7B%22first%22%3A431%2C%22second%22%3A1168%7D%2C%22lines%22%3A%7B%22first%22%3A15%2C%22second%22%3A38%7D%7D&root=%252F): atualizar title, description, Open Graph e Twitter para “planejamento financeiro por conversa”, mantendo `pt-BR`.
- **Modify** [globals.css](air-file://60jn4j480ks6od3snjei/home/macwdo/Codes/pingou-o-que/pingou-o-que-landing-page/app/globals.css?type=file&linesData=%7B%22range%22%3A%7B%22first%22%3A1932%2C%22second%22%3A5007%7D%2C%22lines%22%3A%7B%22first%22%3A49%2C%22second%22%3A134%7D%7D&root=%252F): preservar os tokens claro/escuro e acrescentar somente utilitários de fundo, feedback de pressão e transições de 150–250 ms, com `prefers-reduced-motion`.
- **Modify** [loading.tsx](air-file://60jn4j480ks6od3snjei/home/macwdo/Codes/pingou-o-que/pingou-o-que-landing-page/app/loading.tsx?type=file&linesData=%7B%22range%22%3A%7B%22first%22%3A53%2C%22second%22%3A4679%7D%2C%22lines%22%3A%7B%22first%22%3A2%2C%22second%22%3A105%7D%7D&root=%252F): adaptar o esqueleto à nova estrutura para evitar uma representação obsoleta durante carregamento.

### Lista de acesso

- **Create** `pingou-o-que-landing-page/lib/api/crm.ts`: contrato Zod compartilhado e cliente tipado para `POST /api/crm/leads`.
- **Create** `pingou-o-que-landing-page/app/api/crm/leads/route.ts`: Route Handler que valida o payload e encaminha a inscrição ao Django por `EXPENSE_API_URL`, usando a origem interna já fornecida pelo workspace.
- **Modify** [lead-form.tsx](air-file://60jn4j480ks6od3snjei/home/macwdo/Codes/pingou-o-que/pingou-o-que-landing-page/components/lead-form.tsx?type=file&linesData=%7B%22range%22%3A%7B%22first%22%3A510%2C%22second%22%3A3285%7D%2C%22lines%22%3A%7B%22first%22%3A19%2C%22second%22%3A106%7D%7D&root=%252F): trocar o sucesso simulado por envio real, desabilitar durante submissão e exibir estados de sucesso/erro em região `aria-live`.
- **Modify** [contact-section.tsx](air-file://60jn4j480ks6od3snjei/home/macwdo/Codes/pingou-o-que/pingou-o-que-landing-page/components/contact-section.tsx?type=file&linesData=%7B%22range%22%3A%7B%22first%22%3A495%2C%22second%22%3A2630%7D%2C%22lines%22%3A%7B%22first%22%3A24%2C%22second%22%3A76%7D%7D&root=%252F): transformar a tela em continuação coerente da conversão e retirar o telefone placeholder.
- **Delete** `pingou-o-que-landing-page/stores/landing-store.ts`: remover estado global usado apenas para um valor padrão que nenhum componente altera.
- **Modify** [README.md](air-file://60jn4j480ks6od3snjei/home/macwdo/Codes/pingou-o-que/pingou-o-que-landing-page/README.md?type=file&linesData=%7B%22range%22%3A%7B%22first%22%3A0%2C%22second%22%3A395%7D%2C%22lines%22%3A%7B%22first%22%3A0%2C%22second%22%3A20%7D%7D&root=%252F): documentar a variável server-side e o caminho landing → Route Handler → CRM.

Nenhum arquivo do backend será modificado: o endpoint público de criação já persiste leads em [views.py](air-file://60jn4j480ks6od3snjei/home/macwdo/Codes/pingou-o-que/pingou-o-que-backend/apps/crm/views.py?type=file&linesData=%7B%22range%22%3A%7B%22first%22%3A250%2C%22second%22%3A567%7D%2C%22lines%22%3A%7B%22first%22%3A10%2C%22second%22%3A17%7D%7D&root=%252F), e as mesmas regras de nome, e-mail e objetivo serão refletidas a partir de [serializers.py](air-file://60jn4j480ks6od3snjei/home/macwdo/Codes/pingou-o-que/pingou-o-que-backend/apps/crm/serializers.py?type=file&linesData=%7B%22range%22%3A%7B%22first%22%3A111%2C%22second%22%3A847%7D%2C%22lines%22%3A%7B%22first%22%3A7%2C%22second%22%3A26%7D%7D&root=%252F).

## 4. Implementation Steps

### Task 1: Reescrever a proposta e a arquitetura de conteúdo

1. Reestruturar [landing-content.ts](air-file://60jn4j480ks6od3snjei/home/macwdo/Codes/pingou-o-que/pingou-o-que-landing-page/lib/landing-content.ts?type=file&linesData=%7B%22range%22%3A%7B%22first%22%3A189%2C%22second%22%3A4444%7D%2C%22lines%22%3A%7B%22first%22%3A13%2C%22second%22%3A160%7D%7D&root=%252F) com uma hierarquia de copy: “planeje antes”, três etapas do fluxo, capacidades por domínio, cenários do chat, planos e perguntas.
2. Usar exemplos que o backend suporta: receita planejada e recorrente; despesa única, recorrente ou parcelada; transação real; classificação/conciliação; comparação planejado × realizado.
3. Excluir afirmações sem fonte como Open Finance, categorização totalmente automática, metas persistidas ou números de adoção. Manter os preços e o WhatsApp dentro da seção de oferta, conforme decisão do usuário.
4. Atualizar [layout.tsx](air-file://60jn4j480ks6od3snjei/home/macwdo/Codes/pingou-o-que/pingou-o-que-landing-page/app/layout.tsx?type=file&linesData=%7B%22range%22%3A%7B%22first%22%3A431%2C%22second%22%3A1168%7D%2C%22lines%22%3A%7B%22first%22%3A15%2C%22second%22%3A38%7D%7D&root=%252F) com metadata coerente com a nova promessa.

### Task 2: Construir a narrativa visual minimalista

1. Refazer [hero.tsx](air-file://60jn4j480ks6od3snjei/home/macwdo/Codes/pingou-o-que/pingou-o-que-landing-page/components/hero.tsx?type=file&linesData=%7B%22range%22%3A%7B%22first%22%3A454%2C%22second%22%3A4468%7D%2C%22lines%22%3A%7B%22first%22%3A14%2C%22second%22%3A117%7D%7D&root=%252F) com uma frase curta de valor, subtexto centrado em simplicidade/IA e um CTA primário único; usar o Agoniado como apoio visual, sem deixar o mascote substituir a proposta.
2. Criar `components/product-sections.tsx` para explicar: “ver” versus “planejar”; planejar entradas/compromissos; registrar ou importar o que aconteceu; conciliar e ajustar. Reaproveitar `Badge`, `Button`, `Card` e `FullWidthDivider` já existentes.
3. Compactar [page.tsx](air-file://60jn4j480ks6od3snjei/home/macwdo/Codes/pingou-o-que/pingou-o-que-landing-page/app/page.tsx?type=file&linesData=%7B%22range%22%3A%7B%22first%22%3A645%2C%22second%22%3A11875%7D%2C%22lines%22%3A%7B%22first%22%3A19%2C%22second%22%3A277%7D%7D&root=%252F) para apenas ordenar as seções e evitar repetir grids e espaçamentos.
4. Ajustar [globals.css](air-file://60jn4j480ks6od3snjei/home/macwdo/Codes/pingou-o-que/pingou-o-que-landing-page/app/globals.css?type=file&linesData=%7B%22range%22%3A%7B%22first%22%3A1932%2C%22second%22%3A5007%7D%2C%22lines%22%3A%7B%22first%22%3A49%2C%22second%22%3A134%7D%7D&root=%252F) para dar profundidade com bordas, fundos suaves e uma única cor de destaque; limitar animação a entrada explicativa e feedback de clique, sem movimento contínuo.

### Task 3: Demonstrar o chat sem simular capacidades falsas

1. Criar `components/chat-product-demo.tsx` como a menor ilha client-side, com três botões/tabs nativos controlados por `useState`.
2. Montar cada cenário com componentes visuais simples: balão do usuário, resposta do Agoniado e um resultado estruturado. O cenário de escrita sempre mostrará a etapa “Confirmar/Cancelar” antes do estado concluído, refletindo a aprovação obrigatória configurada em [subagents.py](air-file://60jn4j480ks6od3snjei/home/macwdo/Codes/pingou-o-que/pingou-o-que-backend/apps/ai/subagents.py?type=file&linesData=%7B%22range%22%3A%7B%22first%22%3A409%2C%22second%22%3A1765%7D%2C%22lines%22%3A%7B%22first%22%3A15%2C%22second%22%3A46%7D%7D&root=%252F).
3. Identificar o bloco como “Demonstração” e manter valores de exemplo determinísticos. Não conectar a landing ao agente real, não criar timers e não duplicar a infraestrutura de streaming do produto.
4. Garantir nomes acessíveis, foco visível, seleção anunciada e conteúdo compreensível mesmo com movimento reduzido.

### Task 4: Alinhar navegação, oferta e objeções

1. Atualizar [header-2.tsx](air-file://60jn4j480ks6od3snjei/home/macwdo/Codes/pingou-o-que/pingou-o-que-landing-page/components/ui/header-2.tsx?type=file&linesData=%7B%22range%22%3A%7B%22first%22%3A376%2C%22second%22%3A4435%7D%2C%22lines%22%3A%7B%22first%22%3A12%2C%22second%22%3A159%7D%7D&root=%252F) e [footer.tsx](air-file://60jn4j480ks6od3snjei/home/macwdo/Codes/pingou-o-que/pingou-o-que-landing-page/components/footer.tsx?type=file&root=%252F) para “Como funciona”, “Chat”, “Produto”, “Planos” e “Dúvidas”.
2. Revisar [pricing-section.tsx](air-file://60jn4j480ks6od3snjei/home/macwdo/Codes/pingou-o-que/pingou-o-que-landing-page/components/pricing-section.tsx?type=file&linesData=%7B%22range%22%3A%7B%22first%22%3A397%2C%22second%22%3A5009%7D%2C%22lines%22%3A%7B%22first%22%3A13%2C%22second%22%3A157%7D%7D&root=%252F) para manter os três planos e direcionar todos à lista, sem urgência artificial.
3. Atualizar [faqs-section.tsx](air-file://60jn4j480ks6od3snjei/home/macwdo/Codes/pingou-o-que/pingou-o-que-landing-page/components/faqs-section.tsx?type=file&linesData=%7B%22range%22%3A%7B%22first%22%3A360%2C%22second%22%3A4684%7D%2C%22lines%22%3A%7B%22first%22%3A13%2C%22second%22%3A119%7D%7D&root=%252F) e [contact-section.tsx](air-file://60jn4j480ks6od3snjei/home/macwdo/Codes/pingou-o-que/pingou-o-que-landing-page/components/contact-section.tsx?type=file&linesData=%7B%22range%22%3A%7B%22first%22%3A495%2C%22second%22%3A2630%7D%2C%22lines%22%3A%7B%22first%22%3A24%2C%22second%22%3A76%7D%7D&root=%252F) com respostas e CTA consistentes.
4. Atualizar [loading.tsx](air-file://60jn4j480ks6od3snjei/home/macwdo/Codes/pingou-o-que/pingou-o-que-landing-page/app/loading.tsx?type=file&linesData=%7B%22range%22%3A%7B%22first%22%3A53%2C%22second%22%3A4679%7D%2C%22lines%22%3A%7B%22first%22%3A2%2C%22second%22%3A105%7D%7D&root=%252F) com o mesmo volume visual do hero e da demonstração.

### Task 5: Tornar a lista de acesso funcional

1. Criar `lib/api/crm.ts` com schema Zod derivando o tipo do formulário e validando também a resposta.
2. Criar `app/api/crm/leads/route.ts` para aceitar somente o contrato esperado, encaminhar ao endpoint Django sem expor a origem interna e devolver 422/502 de forma previsível.
3. Atualizar [lead-form.tsx](air-file://60jn4j480ks6od3snjei/home/macwdo/Codes/pingou-o-que/pingou-o-que-landing-page/components/lead-form.tsx?type=file&linesData=%7B%22range%22%3A%7B%22first%22%3A510%2C%22second%22%3A3285%7D%2C%22lines%22%3A%7B%22first%22%3A19%2C%22second%22%3A106%7D%7D&root=%252F) para compartilhar o schema, preservar os dados em falha, impedir duplo envio e limpar somente nome/e-mail após sucesso.
4. Remover o store global sem consumidor real e documentar o contrato operacional em [README.md](air-file://60jn4j480ks6od3snjei/home/macwdo/Codes/pingou-o-que/pingou-o-que-landing-page/README.md?type=file&linesData=%7B%22range%22%3A%7B%22first%22%3A0%2C%22second%22%3A395%7D%2C%22lines%22%3A%7B%22first%22%3A0%2C%22second%22%3A20%7D%7D&root=%252F).

## 5. Acceptance Criteria

1. O hero contém uma proposta de valor de até 10 palavras, menciona planejamento por conversa e apresenta um CTA visível para a lista de acesso.
2. A página explica, sem citar Pierre ou outra marca, que visibilidade mostra o que já aconteceu e que o Pingou o que? também organiza receitas/despesas futuras, compara planejado × realizado e permite agir.
3. A demonstração oferece exatamente três cenários selecionáveis por teclado; cada seleção troca o conteúdo sem recarregar a página.
4. Pelo menos um cenário mostra consulta estruturada e pelo menos um mostra “Confirmar” e “Cancelar” antes de qualquer alteração concluída.
5. A copy apresenta somente capacidades confirmadas pelo código: despesas únicas/recorrentes/parceladas, receitas planejadas, transações manuais/importadas, revisão/classificação/conciliação e operações do chat. Open Finance e metas persistidas não são anunciados como existentes.
6. Os planos mantêm “Gratuito”, “R$ 19,99/mês”, “R$ 49,99/mês” e a oferta de WhatsApp; todos convertem para a lista de acesso.
7. Nenhuma seção usa “mais escolhido”, contagem de clientes, depoimento ou resultado financeiro sem evidência.
8. Um formulário válido envia `POST /api/crm/leads`; com backend disponível recebe 201, exibe sucesso e persiste o lead pelo endpoint CRM existente.
9. Durante o envio, o botão e campos ficam desabilitados; em falha 422/502, os valores digitados permanecem e uma mensagem é anunciada por `aria-live`.
10. Em 375 px e 1440 px não há overflow horizontal, texto cortado ou sobreposição; menu, demonstração, cards de planos e formulário continuam utilizáveis.
11. Tema claro e escuro mantêm contraste legível; com `prefers-reduced-motion: reduce`, transformações decorativas são removidas e nenhuma informação depende de animação.
12. `bun run lint`, `bun run typecheck`, `bun run build` e `git diff --check` terminam sem erros.

## 6. Verification Steps

1. No repositório da landing, executar:
   - `bun run lint`
   - `bun run typecheck`
   - `bun run build`
   - `git diff --check`
2. Iniciar a landing com `bun run dev` para a revisão visual isolada; abrir o preview e verificar hero, âncoras, os três cenários, planos, FAQ e contato.
3. Verificar manualmente em 375 × 812 e 1440 × 900, nos temas claro/escuro e com preferência de movimento reduzido.
4. Navegar somente por teclado: abrir/fechar menu mobile, percorrer os três cenários, abrir FAQ, chegar ao CTA e preencher o formulário; confirmar foco visível e nomes acessíveis.
5. Com o stack integrado já em execução, enviar um lead válido e conferir no Network que `/api/crm/leads` retorna 201. Se o stack não estiver em execução, seguir a skill `$pingou-env` e pedir confirmação antes de `make up`, pois esse comando reseta dados de fixture.
6. Exercitar os erros: campos inválidos não enviam; backend indisponível retorna mensagem recuperável; um segundo clique durante submissão não cria requisição duplicada.
7. Inspecionar a landing final para garantir que não contém “Pierre”, “Open Finance”, “mais escolhido” ou qualquer afirmação de meta persistida.

## 7. Risks & Mitigations

- **A oferta de WhatsApp e os preços não são demonstrados pelo backend atual.** Como o usuário confirmou que são oferta real, eles ficarão restritos à seção comercial/FAQ e não serão apresentados como fluxo técnico já integrado.
- **Uma demonstração estática pode parecer uma conversa ao vivo.** O componente exibirá um rótulo “Demonstração”, usará valores de exemplo e não aceitará texto livre.
- **Copiar a UI autenticada inteira aumentaria dependências e manutenção entre submódulos.** A landing reproduzirá apenas padrões visuais mínimos com seus componentes existentes; nenhuma importação cruzará repositórios.
- **O proxy de CRM pode mascarar falhas do backend.** O Route Handler preservará status de validação, devolverá 502 em indisponibilidade e o formulário manterá o conteúdo para nova tentativa.
- **A voz jovem pode excluir parte do público amplo.** Os headlines serão curtos e contemporâneos, enquanto explicações e FAQs usarão português direto, sem gírias específicas de idade ou renda.