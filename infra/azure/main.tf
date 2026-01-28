terraform {
  required_providers {
    azurerm = {
      source  = "hashicorp/azurerm"
      version = "~> 3.0"
    }
  }
}

provider "azurerm" {
  features {}
}

resource "azurerm_resource_group" "main" {
  name     = "<RESOURCE_GROUP_NAME>"
  location = "<AZURE_REGION>"  # e.g. westeurope, eastus, switzerlandnorth
}

resource "azurerm_container_group" "main" {
  name                = "<CONTAINER_NAME>"
  location            = azurerm_resource_group.main.location
  resource_group_name = azurerm_resource_group.main.name
  os_type             = "Linux"

  container {
    name   = "<CONTAINER_NAME>"
    image  = "<YOUR_DOCKERHUB_USER>/owasp-llm-demo:<TAG>"
    cpu    = "4"
    memory = "4"

    ports {
      port     = 3000
      protocol = "TCP"
    }
  }

  ip_address_type = "Public"
  dns_name_label  = "<UNIQUE_DNS_NAME>"
}

output "url" {
  value = "http://${azurerm_container_group.main.fqdn}:3000"
}

output "tunnel_url" {
  value       = "Check container logs for HTTPS tunnel URL"
  description = "Cloudflare Tunnel URL (dynamic, see logs)"
}

output "logs_command" {
  value       = "az container logs --resource-group <RESOURCE_GROUP_NAME> --name <CONTAINER_NAME> | grep 'HTTPS Tunnel'"
  description = "Command to retrieve tunnel URL from logs"
}
