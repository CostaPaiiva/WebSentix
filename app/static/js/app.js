// 1. Aguarda o carregamento completo do DOM antes de executar qualquer lógica.
// 2. Seleciona os botões de abas (".tab-btn") e os painéis de modo (".mode-panel") para controlar a interface.
// 3. Configura o campo oculto "input_type" para armazenar o tipo de entrada selecionado (texto, URL ou arquivo).
// 4. Adiciona eventos de clique nos botões para alternar entre modos, ativando o painel correspondente e destacando o botão ativo.
// 5. Atualiza dinamicamente o valor do campo "input_type" conforme o modo escolhido pelo usuário.
// 6. Adiciona evento de submissão ao formulário de análise para exibir o indicador de carregamento ("loading-indicator").
// 7. Garante uma experiência interativa: alterna abas, mostra o painel correto e sinaliza ao usuário que o processamento está em andamento.


// Aguarda o carregamento completo do DOM antes de executar o código
document.addEventListener("DOMContentLoaded", function () {
    
    // Seleciona todos os botões de abas (tabs) pela classe "tab-btn"
    const buttons = document.querySelectorAll(".tab-btn");
    // Seleciona todos os painéis de modo pela classe "mode-panel"
    const panels = document.querySelectorAll(".mode-panel");
    // Seleciona o campo oculto que guarda o tipo de entrada
    const inputType = document.getElementById("input_type");
    // Seleciona o formulário principal de análise
    const form = document.getElementById("analysis-form");
    // Seleciona o indicador de carregamento
    const loading = document.getElementById("loading-indicator");

    // Para cada botão de aba encontrado
    buttons.forEach((button) => {
        // Adiciona evento de clique ao botão
        button.addEventListener("click", () => {
            // Obtém o modo associado ao botão (via atributo data-mode)
            const mode = button.dataset.mode;

            // Remove a classe "active" de todos os botões
            buttons.forEach((btn) => btn.classList.remove("active"));
            // Adiciona a classe "active" apenas ao botão clicado
            button.classList.add("active");

            // Remove a classe "active" de todos os painéis
            panels.forEach((panel) => panel.classList.remove("active"));
            // Seleciona o painel correspondente ao modo clicado
            const activePanel = document.getElementById(`panel-${mode}`);
            // Se o painel existir, adiciona a classe "active" para exibi-lo
            if (activePanel) {
                activePanel.classList.add("active");
            }

            // Atualiza o campo oculto "input_type" com o modo selecionado
            if (inputType) {
                inputType.value = mode;
            }
        });
    });

    // Se o formulário existir
    if (form) {
        // Adiciona evento de submissão ao formulário
        form.addEventListener("submit", () => {
            // Se o indicador de carregamento existir
            if (loading) {
                // Remove a classe "hidden" para mostrar o indicador de carregamento
                loading.classList.remove("hidden");
            }
        });
    }
});
