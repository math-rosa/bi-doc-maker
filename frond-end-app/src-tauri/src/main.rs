#![cfg_attr(not(debug_assertions), windows_subsystem = "windows")]

use serde_json::Value;
use std::process::Command as SystemCommand;
use tauri::api::process::Command as SidecarCommand;

const SIDECAR_NAME: &str = "documentador-core";

#[tauri::command]
fn ping() -> String {
    "pong".to_string()
}

use std::path::Path;

fn validate_path(path_str: &str) -> Result<String, String> {
    let path = Path::new(path_str);
    if path_str.contains("..") {
        return Err("O caminho possui '../' que nao e permitido.".to_string());
    }
    match path.canonicalize() {
        Ok(canonical_path) => Ok(canonical_path.to_string_lossy().to_string()),
        Err(e) => Err(format!("Falha ao resolver caminho (pode nao existir): {}", e)),
    }
}

fn open_cross_platform(path: String) -> Result<(), String> {
    let cmd = if cfg!(target_os = "windows") {
        SystemCommand::new("explorer.exe").arg(path).spawn()
    } else if cfg!(target_os = "macos") {
        SystemCommand::new("open").arg(path).spawn()
    } else {
        SystemCommand::new("xdg-open").arg(path).spawn()
    };

    cmd.map(|_| ()).map_err(|error| format!("Falha ao abrir: {error}"))
}

#[tauri::command]
async fn analyze_project(path: String) -> Result<Value, String> {
    let valid_path = validate_path(&path)?;
    run_core_async(vec![
        "analyze".to_string(),
        "--project".to_string(),
        valid_path,
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
    
    let valid_path = validate_path(&path)?;
    let valid_output_dir = validate_path(&output_dir)?;

    let mut args = vec![
        "export".to_string(),
        "--project".to_string(),
        valid_path,
        "--output-dir".to_string(),
        valid_output_dir,
        "--formats".to_string(),
        formats.join(","),
        "--json".to_string(),
    ];

    if let Some(branding_payload) = branding {
        args.push("--branding-json".to_string());
        args.push(branding_payload.to_string());
    }

    run_core_async(args).await
}

#[tauri::command]
fn open_output_folder(path: String) -> Result<(), String> {
    if path.trim().is_empty() {
        return Err("Pasta de saida nao informada.".to_string());
    }
    let valid_path = validate_path(&path)?;
    open_cross_platform(valid_path)
}

#[tauri::command]
fn open_output_file(path: String) -> Result<(), String> {
    if path.trim().is_empty() {
        return Err("Arquivo nao informado.".to_string());
    }
    let valid_path = validate_path(&path)?;
    open_cross_platform(valid_path)
}

#[tauri::command]
fn open_external_url(url: String) -> Result<(), String> {
    let url = url.trim().to_string();
    let allowed = [
        "https://www.linkedin.com/in/mathrosa96/",
        "https://github.com/math-rosa/bi-doc-maker",
        "https://nubank.com.br/cobrar/5iu9s/69ff8e6c-3a76-4fa3-9a60-d3b2e1e8885c",
    ];

    if !allowed.iter().any(|allowed_url| url == *allowed_url) {
        return Err("Link externo nao permitido.".to_string());
    }

    open_cross_platform(url)
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
            ping,
            analyze_project,
            export_project,
            open_output_folder,
            open_output_file,
            open_external_url
        ])
        .run(tauri::generate_context!())
        .expect("error while running tauri application");
}
