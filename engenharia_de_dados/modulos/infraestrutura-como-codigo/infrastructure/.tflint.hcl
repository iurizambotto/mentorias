config {
  # Modules are validated on their own, from their own directory.
  call_module_type = "local"
}

plugin "terraform" {
  enabled = true
  preset  = "recommended"
}
