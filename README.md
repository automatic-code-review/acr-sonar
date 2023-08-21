# acr-sonar

Extensao que roda o sonar-scanner sobre as alteracoes do merge request, as validacoes em si vao depender das configuracoes no sonar para a languagem em questao

1. Propriedade url se refere da url do servidor do sonar qube
2. Propriedade token se refere ao token de autenticacao tanto para o sonar-scanner como para a autenticacao com a api, caso seja usado o auth_type como BEARER_TOKEN
3. Propriedade auth_type se refere ao tipo de autenticacao, quando for BEREAR_TOKEN funciona informando apenas o token, ja quando usado BASIC_AUTH necessario o auth_password e auth_username
4. Propriedade scanner_home se refere ao caminho da pasta do sonar-scanner, deve ser uma pasta antes do /bin aonde fica o sonar-scanner
5. Propriedade auth_username se refere ao nome de usuario para autenticacao quando usado BASIC_AUTH
6. Propriedade auth_password se refere a senha do usuario para autenticacao quando usado BASIC_AUTH
7. Propriedade rules se refere a lista de validacoes que devem de fato ser comentada no merge request, caso o sonar qube identifique-as

Arquivo config.json

```json
{
    "url": "",
    "token": "",
    "auth_type": "BASIC_AUTH",
    "scanner_home": "",
    "auth_username": "",
    "auth_password": "",
    "rules": [

    ]
}
```
