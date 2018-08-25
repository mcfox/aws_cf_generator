  class AwscfGenerator < Rails::Generators::Base
  source_root File.expand_path('../templates', __FILE__)
  argument :app_name, :type => :string, :default => "application"
  argument :roles, :type => :array

  def generate_layout
    copy_file "nginx/app_nginx.conf", "aws/nginx/app_nginx.conf"
    copy_file "nginx/nginx_default.conf", "aws/nginx/nginx_default.conf"
    copy_file "geradores/app-ami-generator.py", "aws/geradores/app-ami-generator.py"
    copy_file "geradores/app-stack-generator.py", "aws/geradores/app-stack-generator.py"
    copy_file "geradores/build_tempaltes.sh", "aws/geradores/build_tempaltes.sh"
    copy_file "scripts/app_deploy.sh", "aws/scripts/app_deploy.sh"
    copy_file "scripts/app_pack.sh", "aws/scripts/app_pack.sh"
    copy_file "scripts/app_stop_instances_by_role.sh", "aws/scripts/app_stop_instances_by_role.sh"
    copy_file "scripts/app_update.sh", "aws/scripts/app_update.sh"
    copy_file "scripts/run_delayed_jobs.sh", "aws/scripts/run_delayed_jobs.sh"
  end

  private

  def file_name
    app_name.underscore
  end
end
