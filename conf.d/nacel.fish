# Nacel AI Plugin Loader for Fish (Fisher, Oh My Fish, conf.d)
set -l plugin_dir (path dirname (path dirname (status filename)))
if test -f "$plugin_dir/nacel.fish"
    source "$plugin_dir/nacel.fish"
end
