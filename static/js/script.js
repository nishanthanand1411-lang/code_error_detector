const editor = document.getElementById("code");
const sampleButton = document.getElementById("sample-btn");
const clearButton = document.getElementById("clear-btn");

if (sampleButton && editor) {
  sampleButton.addEventListener("click", () => {
    editor.value = "def greet(name):\n    print('Hello, ' + nme)\n\ngreet('world')\n";
    editor.focus();
  });
}
if (clearButton && editor) {
  clearButton.addEventListener("click", () => {
    editor.value = "";
    editor.focus();
  });
}
