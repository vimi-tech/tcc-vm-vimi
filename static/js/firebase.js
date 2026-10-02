import { initializeApp } from "https://www.gstatic.com/firebasejs/10.12.0/firebase-app.js";
import {
  getAuth, GoogleAuthProvider, signInWithPopup, signInWithRedirect,
  getRedirectResult, onAuthStateChanged, signOut
} from "https://www.gstatic.com/firebasejs/10.12.0/firebase-auth.js";
import { getFirestore, doc, getDoc }
  from "https://www.gstatic.com/firebasejs/10.12.0/firebase-firestore.js";
 
// ===== Configuração do Firebase =====
const firebaseConfig = {
  apiKey: "AIzaSyDDQ9YzAQDNgckD4aduLJVoiVqWZlJUGbI",
  authDomain: "tccfeirascore.firebaseapp.com",
  projectId: "tccfeirascore",
  storageBucket: "tccfeirascore.firebasestorage.app",
  messagingSenderId: "1035321887089",
  appId: "1:1035321887089:web:82ea49098838822479ced0"
};
 
const app = initializeApp(firebaseConfig);
const auth = getAuth(app);
const db = getFirestore(app);
auth.languageCode = "pt-BR";
 
const provider = new GoogleAuthProvider();
provider.setCustomParameters({ prompt: "select_account" });
 
// ===== Elementos da página =====
const $ = (id) => document.getElementById(id);
const form = $("voteForm");
const btnGoogle = $("btn-google");
const btnVotar = $("btn-votar");
const msg = $("msg-status");
 
// ===== ID do aparelho (fica salvo no navegador) =====
function gerarUUID() {
  // Navegadores em endereço seguro (https ou localhost)
  if (window.crypto && typeof crypto.randomUUID === "function") {
    return crypto.randomUUID();
  }
  // Alternativa para http pelo IP da rede (ex.: celular acessando o computador)
  const bytes = crypto.getRandomValues(new Uint8Array(16));
  bytes[6] = (bytes[6] & 0x0f) | 0x40; // versão 4
  bytes[8] = (bytes[8] & 0x3f) | 0x80; // variante
  const hex = Array.from(bytes, (b) => b.toString(16).padStart(2, "0")).join("");
  return `${hex.slice(0, 8)}-${hex.slice(8, 12)}-${hex.slice(12, 16)}-${hex.slice(16, 20)}-${hex.slice(20)}`;
}
 
function obterIdDispositivo() {
  let id = localStorage.getItem("idDispositivo");
  if (!id) {
    id = gerarUUID();
    localStorage.setItem("idDispositivo", id);
  }
  return id;
}
 
const idDispositivo = obterIdDispositivo();
$("campo-dispositivo").value = idDispositivo;
 
// ===== Mensagens de erro em português =====
function traduzirErro(codigo) {
  const erros = {
    "auth/popup-closed-by-user": "A janela do Google foi fechada antes de terminar. Tente de novo.",
    "auth/cancelled-popup-request": "Já existe uma janela de login aberta.",
    "auth/unauthorized-domain": "Este endereço não está autorizado no Firebase.",
    "auth/network-request-failed": "Sem conexão com a internet. Verifique e tente de novo.",
    "auth/operation-not-allowed": "O login com Google não está ativado no Firebase.",
  };
  return erros[codigo] || "Não foi possível entrar (" + codigo + ").";
}
 
// ===== Bloqueia a tela se o aparelho já votou =====
function bloquearAparelho() {
  msg.textContent = "Este aparelho já registrou um voto. Obrigado por participar!";
  form.style.display = "none";
  btnVotar.style.display = "none";
}
 
// ===== Botão do Google: entrar ou trocar de conta =====
btnGoogle.addEventListener("click", async () => {
  msg.textContent = "";
  try {
    if (auth.currentUser) await signOut(auth);
    await signInWithPopup(auth, provider);
  } catch (erro) {
    if (erro.code === "auth/popup-blocked" ||
        erro.code === "auth/operation-not-supported-in-this-environment") {
      await signInWithRedirect(auth, provider);
    } else {
      msg.textContent = traduzirErro(erro.code);
    }
  }
});
 
// ===== Botão VOTAR: pega um token novo e envia o formulário ao Flask =====
form.addEventListener("submit", async (evento) => {
  evento.preventDefault();
  if (!auth.currentUser) return;
 
  btnVotar.disabled = true;
  try {
    $("campo-token").value = await auth.currentUser.getIdToken(true);
    $("campo-dispositivo").value = idDispositivo;
    form.submit();
  } catch (erro) {
    msg.textContent = "Não foi possível confirmar seu login. Tente entrar de novo.";
    btnVotar.disabled = false;
  }
});
 
// ===== Início: checa o aparelho e depois acompanha o login =====
async function iniciar() {
  try {
    const registro = await getDoc(doc(db, "dispositivos", idDispositivo));
    if (registro.exists()) {
      bloquearAparelho();
      return;
    }
  } catch (erro) {
    console.warn("Não foi possível checar o aparelho:", erro.code);
  }
 
  getRedirectResult(auth).catch((erro) => {
    msg.textContent = traduzirErro(erro.code);
  });
 
  onAuthStateChanged(auth, (usuario) => {
    if (usuario) {
      msg.textContent = "Conectado como " + (usuario.displayName || usuario.email) + ".";
      $("texto-btn-google").textContent = "USAR OUTRA CONTA";
      btnVotar.disabled = false;
    } else {
      $("texto-btn-google").textContent = "ENTRAR COM O GOOGLE";
      $("campo-token").value = "";
      btnVotar.disabled = true;
    }
  });
}
 
iniciar();