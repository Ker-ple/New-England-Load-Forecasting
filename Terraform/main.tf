data "template_file" "iso_pipeline" {
    template = "${file("${path.root}/ISO.asl.yaml.tftpl")}"
    vars = {
        iso_load_lambda_arn = 
    }
}