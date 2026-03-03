function updateFileName(input) {
    const fileName = input.files.length > 0 ? input.files[0].name : "Nenhum arquivo escolhido";
    document.getElementById('file-name').textContent = fileName;
}