// Script global para a aplicação

// Fechar alertas automaticamente após 5 segundos
document.addEventListener('DOMContentLoaded', function() {
    const alerts = document.querySelectorAll('.alert');
    
    alerts.forEach(alert => {
        setTimeout(() => {
            alert.style.opacity = '0';
            setTimeout(() => alert.remove(), 300);
        }, 5000);
    });
});

// Confirmação de eliminação genérica
function confirmarEliminacao(mensagem = "Tem a certeza?") {
    return confirm(mensagem);
}

// Formatação de números
function formatarNumero(numero, casasDecimais = 4) {
    if (numero === null || numero === undefined) return 'N/A';
    return parseFloat(numero).toFixed(casasDecimais);
}

// Formatação de bytes
function formatarBytes(bytes) {
    if (bytes === null || bytes === undefined) return 'N/A';
    
    bytes = parseInt(bytes);
    
    if (bytes < 1024) {
        return `${bytes} B`;
    } else if (bytes < 1024 * 1024) {
        return `${(bytes / 1024).toFixed(2)} KB`;
    } else {
        return `${(bytes / (1024 * 1024)).toFixed(2)} MB`;
    }
}