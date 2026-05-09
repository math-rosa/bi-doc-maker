#![cfg_attr(not(debug_assertions), windows_subsystem = "windows")]

use serde_json::Value;
use std::process::Command as SystemCommand;
use tauri::api::process::Command as SidecarCommand;

const SIDECAR_NAME: &str = "documentador-core";

#[tauri::command]
async fn analyze_project(path: String) -> Result<Value, String> {
    run_core_async(vec![
        "analyze".to_string(),
        "--project".to_string(),
        path,
        "--json".to_string(),
    ]).await
}

#[tauri::command]
async fn export_project(
    path: String,
    output_dir: String,
    formats: Vec<String>,
    branding: Option<Value>,
) -> Result<Value, String> {
    if formats.is_empty() {
        return Err("Selecione pelo menos um formato de exportacao.".to_string());
    }

    let mut args = vec![
        "export".to_string(),
        "--project".to_string(),
        path,
        "--output-dir".to_string(),
        output_dir,
        "--formats".to_string(),
        formats.join(","),
        "--json".to_string(),
    ];

    if let Some(branding) = branding {
        if !branding.is_null() {
            args.push("--branding-json".to_string());
            args.push(branding.to_string());
        }
    }

    run_core_async(args).await
}

#[tauri::command]
fn open_output_folder(path: String) -> Result<(), String> {
    if path.trim().is_empty() {
        return Err("Pasta de saida nao informada.".to_string());
    }

    SystemCommand::new("explorer.exe")
        .arg(path)
        .spawn()
        .map(|_| ())
        .map_err(|error| format!("Falha ao abrir a pasta de saida: {error}"))
}

#[tauri::command]
fn open_output_file(path: String) -> Result<(), String> {
    if path.trim().is_empty() {
        return Err("Arquivo nao informado.".to_string());
    }

    SystemCommand::new("explorer.exe")
        .arg(path)
        .spawn()
        .map(|_| ())
        .map_err(|error| format!("Falha ao abrir o arquivo gerado: {error}"))
}

#[tauri::command]
fn open_external_url(url: String) -> Result<(), String> {
    let url = url.trim();
    let allowed = [
        "https://github.com/math-rosa/bi-doc-maker",
        "https://www.linkedin.com/in/mathrosa96/",
    ];

    if !allowed.contains(&url) {
        return Err("Link externo nao permitido.".to_string());
    }

    SystemCommand::new("explorer.exe")
        .arg(url)
        .spawn()
        .map(|_| ())
        .map_err(|error| format!("Falha ao abrir o link no navegador: {error}"))
}

async fn run_core_async(args: Vec<String>) -> Result<Value, String> {
    tauri::async_runtime::spawn_blocking(move || run_core_blocking(args))
        .await
        .map_err(|error| format!("Falha ao aguardar o core Python: {error}"))?
}

fn run_core_blocking(args: Vec<String>) -> Result<Value, String> {
    let output = SidecarCommand::new_sidecar(SIDECAR_NAME)
        .map_err(|error| format!("Falha ao localizar o sidecar Python: {error}"))?
        .args(args)
        .output()
        .map_err(|error| format!("Falha ao executar o sidecar Python: {error}"))?;

    let stdout = output.stdout.trim();
    let stderr = output.stderr.trim();

    if stdout.is_empty() {
        return Err(if stderr.is_empty() {
            "O core Python nao retornou resposta.".to_string()
        } else {
            stderr.to_string()
        });
    }

    let payload: Value = serde_json::from_str(stdout).map_err(|error| {
        let detalhe = if stderr.is_empty() {
            stdout.to_string()
        } else {
            format!("{stdout}\n\nLogs:\n{stderr}")
        };
        format!("O core Python retornou JSON invalido: {error}\n{detalhe}")
    })?;

    let ok = payload
        .get("ok")
        .and_then(Value::as_bool)
        .unwrap_or(false);

    if !output.status.success() || !ok {
        return Err(payload
            .get("error")
            .and_then(Value::as_str)
            .map(str::to_string)
            .unwrap_or_else(|| {
                if stderr.is_empty() {
                    "Falha ao processar o projeto no core Python.".to_string()
                } else {
                    stderr.to_string()
                }
            }));
    }

    Ok(payload)
}

fn main() {
    tauri::Builder::default()
        .invoke_handler(tauri::generate_handler![
            analyze_project,
            export_project,
            open_output_folder,
            open_output_file,
            open_external_url
        ])
        .run(tauri::generate_context!())
        .expect("error while running tauri application");
}
