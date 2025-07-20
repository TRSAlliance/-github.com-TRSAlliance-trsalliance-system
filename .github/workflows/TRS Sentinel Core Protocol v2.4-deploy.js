name: 🛡️ TRS Sentinel Core Protocol v2.4-deploy.js

on:
  workflow_dispatch:
    inputs:
      auth_token:
        description: '🔐 24-char TRS Auth Token'
        required: true
  push:
    branches: [ main ]
    paths:
      - 'src/**'
      - 'scripts/**'
      - '.github/workflows/main.yml'

env:
  TRS_VERSION: '2.4.1'
  NODE_VERSION: '20.14.1'
  SEAL_EXPIRY: '24h'
  FIREWALL: 'enforced'

jobs:
  authentication:
    name: 🔒 Quantum Authentication
    runs-on: ubuntu-22.04
    outputs:
      crypto_seal: ${{ steps.generate_seal.outputs.seal }}
      threat_level: ${{ steps.threat_scan.outputs.level }}
    steps:
      - name: Verify TRS Token
        run: |
          if [[ "${{ github.event.inputs.auth_token }}" != "${{ secrets.TRS_QUANTUM_KEY }}" ]]; then
            echo "::error::TRS VIOLATION: Invalid Quantum Token"
            echo "This incident has been reported to Sentinel Command"
            exit 137
          fi

      - name: Checkout (Airgap Mode)
        uses: actions/checkout@v4
        with:
          ssh-key: ${{ secrets.TRS_DEPLOY_KEY }}
          persist-credentials: false

      - name: Generate Quantum Seal
        id: generate_seal
        uses: ./.github/actions/quantum-seal
        with:
          commit_hash: ${{ github.sha }}
          expiry: ${{ env.SEAL_EXPIRY }}
        env:
          TRS_CRYPTO_KEY: ${{ secrets.TRS_SEAL_KEY }}

  deployment:
    name: 🚀 TRS Core Deployment
    needs: authentication
    runs-on: trs-armed-runner
    environment: production
    timeout-minutes: 18
    steps:
      - name: Validate Quantum Seal
        run: |
          node ./scripts/validate-seal.js \
            --seal '${{ needs.authentication.outputs.crypto_seal }}' \
            --max-age ${{ env.SEAL_EXPIRY }}

      - name: Deploy Core Systems
        uses: ./.github/actions/trs-deploy
        with:
          firewall: ${{ env.FIREWALL }}
          seal: ${{ needs.authentication.outputs.crypto_seal }}
        env:
          TRS_NETWORK_KEY: ${{ secrets.TRS_NETWORK_KEY }}

  monitoring:
    name: 📡 Sentinel Monitoring
    needs: deployment
    if: always()
    runs-on: ubuntu-22.04
    steps:
      - name: Report Deployment Status
        uses: ./.github/actions/sentinel-report
        with:
          seal: ${{ needs.authentication.outputs.crypto_seal }}
          status: ${{ job.status }}
        env:
          SENTINEL_API_KEY: ${{ secrets.TRS_SENTINEL_API }}
