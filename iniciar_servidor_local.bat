@echo off
chcp 65001 > nul
title Servidor Local de Testes - Publicoverso

echo ==========================================================
echo  Iniciando Servidor Local de Testes do Publicoverso
echo ==========================================================
echo.

where python >nul 2>nul
if %errorlevel% neq 0 (
    echo [ERRO] Interpretador Python nao foi encontrado no PATH.
    echo Por favor, instale o Python ou adicione-o as variaveis de ambiente.
    pause
    exit /b 1
)

echo Python detectado. Subindo servidor na porta 8088...
echo O navegador padrao sera aberto em http://localhost:8088
echo.

python "%~dp0server.py"

pause
