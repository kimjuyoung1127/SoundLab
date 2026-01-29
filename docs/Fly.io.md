fly mcp launch
Launching an npx, uvx, go run or docker image stdio MCP server into a Fly machine and configuring a MCP client to connect to it is a one-step process. The fly mcp launch command will create a new Fly machine, install the MCP server, and configure the MCP client to connect to it.

Wrap textCopy to clipboard
fly mcp launch "uvx mcp-server-time" --claude --server time
The above command specifies the command to run in the machine, selects the claude client to be the one to be configured using the server name time.

Support for Claude, Cursor, Neovim, VS Code, Windsurf, and Zed are built in. You can also provide the path to the configuration file. You can also provide multiple clients and configuration files at once.

By default, bearer token authentication will be set up on both the server and client, though there are other options and this can be disabled.

You can configure auto-stop, file contents, flycast, secrets, region, and vm sizes.

See Examples for a number of examples.

See the fly mcp launch documentation for more details on the command and its options.

Inspect
You can use the MCP Inspector to test and debug your MCP server:

As the MCP inspector is a Node.js application, you need to Download and install Node.js first. MacOS users can use brew install node.

Wrap textCopy to clipboard
fly mcp inspect --claude --server time
This command is simply a convenience, all it does is run the inspector set up to connect to the same machine, authentication, and arguments as the MCP client (in this case, Claude) would.

Destroy
When you no longer need the MCP, you can destroy it:

Wrap textCopy to clipboard
fly mcp destroy --claude --server time
This will also remove the configuration entry from the MCP client.

MCP Transports
The MCP standard define two types of base transports: stdio and Streaming HTTP. Previously there was also a Server Sent Events (SSE) transport; this is now deprecated but still supported by a number of tools.

At the present time, MCPs that implement the stdio transport are by far most common, most interoperable, and is the transport we recommend.

Below are instructions on how to deploy each of these transport mechanisms on Fly.io using the Everything MCP Server provided by Anthropic which attempts to exercise all the features of the MCP protocol. It is not intended to be a useful server, but rather a test server for builders of MCP clients. It implements prompts, tools, resources, sampling, and more to showcase MCP capabilities.. It currently supports stdio, SSE, and Streaming HTTP.

One thing worth trying independent of the transport method you chose is the printEnv tool. From the inspector click on tools at the top, then List Tools, then printEnv, and finally Run Tool.

stdio
This guide shows you how to wrap and proxy a stdio MCP server so that it can be deployed remotely.

SSE
SSE servers can be deployed as is.

Streaming HTTP
Streaming HTTP servers can be deployed as is.
stdio
Beta documentation. This documentation has been recently released, but may still need improvements and clarifications. Please provide feedback for this documentation in our community forums or edit on github.

stdio MCP servers are not intended to be run remotely, but fly mcp provides the ability to proxy and wrap them.

The data flow is tthat the proxy is a stdio MCP that forwards requests to a wrapper MCP (basically a slimmed down and streamlined Streamable HTTP server), which in turn forwards requests to a stdio MCP running on a remote server:

MCP Proxy/Wrapper data flow

Start by cloning the MCP servers git repository and making a copy of the Dockerfile:

Wrap textCopy to clipboard
git clone https://github.com/modelcontextprotocol/servers.git
cd servers
cp src/everything/Dockerfile .
Make the following changes to the Dockerfile:

Wrap textCopy to clipboard
 RUN npm ci --ignore-scripts --omit-dev
+
+COPY --from=flyio/flyctl /flyctl /usr/bin
+ENTRYPOINT [ "/usr/bin/flyctl", "mcp", "wrap", "--" ]
+EXPOSE 8080

 CMD ["node", "dist/index.js"]
Now run:

Wrap textCopy to clipboard
fly launch --ha=false
Access the MCP server via the MCP inspector:

Wrap textCopy to clipboard
fly mcp proxy -i
An example claude_desktop_config.json:

Wrap textCopy to clipboard
{
  "mcpServers": {
    "filesystem": {
      "command": "/Users/rubys/.fly/bin/flyctl",
      "args": [
         "mcp",
         "proxy",
         "--url=https://mcp.fly.dev/"
       ]
    }
  }
}
SSE
Beta documentation. This documentation has been recently released, but may still need improvements and clarifications. Please provide feedback for this documentation in our community forums or edit on github.

SSE servers can be run as is, we just need to identify the port used and adjust the command, and disable the smoke checks as they will confuse the server.

Start by cloning the MCP servers git repository and making a copy of the Dockerfile:

Wrap textCopy to clipboard
git clone https://github.com/modelcontextprotocol/servers.git
cd servers
cp src/everything/Dockerfile .
Make the following changes to the Dockerfile:

Wrap textCopy to clipboard
 RUN npm ci --ignore-scripts --omit-dev
+
+EXPOSE 3001

-CMD ["node", "dist/index.js"]
+CMD ["node", "dist/sse.js"]
Now run:

Wrap textCopy to clipboard
fly launch --ha=false --smoke-checks=false
Access the MCP server via the MCP inspector:

Wrap textCopy to clipboard
npx @modelcontextprotocol/inspector
In the top left, change the transport type to SSE.

Set the URL to match your application, where the URL will be of the form:

Wrap textCopy to clipboard
https://appname.fly.dev/sse
Replace the appname with the name of your application, but keep the https:// and /sse.

Click Connect.

An example Cursor configuration:

Wrap textCopy to clipboard
{
  "mcpServers": {
    "everything": {
      "url": "https://appname.fly.dev/sse",
      "env": {}
    }
  }
}
With SSE transports, fly mcp proxy may not be required, but could be useful if:

Your MCP client doesn’t support SSE
You need to set up a wireguard tunnel to access your MCP serever via an .internal or .proxy address.
You need to route the request to a specific machine.
Streaming HTTP
Beta documentation. This documentation has been recently released, but may still need improvements and clarifications. Please provide feedback for this documentation in our community forums or edit on github.

Streaming HTTP servers can be run as is, we just need to identify the port used and adjust the command, and disable the smoke checks as they will confuse the server.

Start by cloning the MCP servers git repository and making a copy of the Dockerfile:

Wrap textCopy to clipboard
git clone https://github.com/modelcontextprotocol/servers.git
cd servers
cp src/everything/Dockerfile .
Make the following changes to the Dockerfile:

Wrap textCopy to clipboard
 RUN npm ci --ignore-scripts --omit-dev
+
+EXPOSE 3001

-CMD ["node", "dist/index.js"]
+CMD ["node", "dist/streamableHttp.js"]
Now run:

Wrap textCopy to clipboard
fly launch --ha=false --smoke-checks=false
Access the MCP server via the MCP inspector:

Wrap textCopy to clipboard
npx @modelcontextprotocol/inspector
In the top left, change the transport type to Streamable HTTP.

Set the URL to match your application, where the URL will be of the form:

Wrap textCopy to clipboard
https://appname.fly.dev/mcp
Replace the appname with the name of your application, but keep the https:// and /mcp.

Click Connect.

An example Cursor configuration:

Wrap textCopy to clipboard
{
  "mcpServers": {
    "everything": {
      "url": "https://appname.fly.dev/mcp",
      "env": {}
    }
  }
}
With Streaming HTTP transports, fly mcp proxy may not be required, but could be useful if:

Your MCP client doesn’t support Streaming HTTP
You need to set up a wireguard tunnel to access your MCP serever via an .internal or .proxy address.
You need to route the request to a specific machine.
fly launch
Beta documentation. This documentation has been recently released, but may still need improvements and clarifications. Please provide feedback for this documentation in our community forums or edit on github.

Fly launch is a bundle of features that take a lot of the work out of deploying and managing your Fly App.

This guide presumes that you have flyctl installed, and have successfully run either fly auth signup or fly auth login.

The first step is intended to be run in an empty directory.

Create your app
Create a Dockerfile with the following contents:

Wrap textCopy to clipboard
FROM flyio/mcp
VOLUME /data
CMD [ "npx", "-f", "@modelcontextprotocol/server-filesystem", "/data/" ]
Now use the fly launch command:

Wrap textCopy to clipboard
fly launch
Optional parameters include --name, --org, and --flycast.

Review and accept the defaults.

The Dockerfile will be build, and the resulting image will be pushed and deployed. In the process, a volume will be allocated and both a shared ipv4 and a dedicated ipv6 address will be allocated.

Your configuration will be found in fly.toml.

If you make any change to your Dockerfile or fly.toml, run fly deploy to apply the changes.

Accessing the MCP via an inspector
As the MCP inspector is a Node.js application, you need to Download and install Node.js first. MacOS users can use brew install node.

You are test out your MCP server using the MCP inspector:

Wrap textCopy to clipboard
fly mcp proxy -i
Navigate to http://127.0.0.1:6274 ; click Connect; then List Tools; select any tool; fill out the form (if any) and click Run tool.

Configure your LLM
Here’s an example claude_desktop_config.json:

Wrap textCopy to clipboard
{
  "mcpServers": {
    "filesystem": {
      "command": "/Users/rubys/.fly/bin/flyctl",
      "args": [
         "mcp",
         "proxy",
         "--url=https://mcp.fly.dev/"
       ]
    }
  }
}
Adjust the flyctl path and the value of the –url, restart your LLM (in this case, Claude) and try out the tools.
Machines API
Beta documentation. This documentation has been recently released, but may still need improvements and clarifications. Please provide feedback for this documentation in our community forums or edit on github.

The Machines API is a low level interface that provides access to the full range of platform services. It consists of a set of REST and a GraphQL interfaces. You can access these from any programming language capable of producing HTTP GET and POST requests and the ability to generate and parse JSON.

An example of when you would want to use the Machines API is when you want to create a Per-User Dev Environment

This guide presumes that you are running MacOS, Linux, or WSL2, and have curl installed.

Select an organization
All Fly.io users have a personal organization and may be a member of other organizations. Set an environment variable with your choice.

Wrap textCopy to clipboard
export ORG="personal"
Organization token
To get started, you need an organization token, which you can obtain via the dashboard.

Go to https://fly.io/dashboard, change the organization if necessary, select Tokens from the list on the left hand side of the page, optionally enter a token name or an expiration period and click on Create Organization token. Once complete you should see something like the following:

Obtaining an organization token via the dashboard

Click on Copy to clipboard, and then run the following command with your token pasted inside the quotes:

Wrap textCopy to clipboard
export FLY_API_TOKEN="FlyV1 fm2_IJPECAAA..."
Select an API hostname
The host name you chose depends on whether your application is running inside or outside your Fly.io private Wireguard network. If you are not sure, use the public base URL:

Wrap textCopy to clipboard
export FLY_API_HOSTNAME=https://api.machines.dev
Chose a hostname for your app
You are free to chose any available hostname for your application. The following will generate a name that is likely to be unique:

Wrap textCopy to clipboard
export APP_NAME=mcp-demo-$(uuidgen | cut -d '-' -f 5 | tr A-Z a-z)
Create your app
Now use the Create a Fly App API:

Wrap textCopy to clipboard
curl -i -X POST \
  -H "Authorization: Bearer ${FLY_API_TOKEN}" \
  -H "Content-Type: application/json" \
  "${FLY_API_HOSTNAME}/v1/apps" \
  -d "{ \
      \"app_name\": \"${APP_NAME}\", \
      \"org_slug\": \"${ORG}\" \
    }"
Response should be a 200 Success, along with some JSON output.

Create IP addresses for your application
While the Fly.io GraphQL endpoint is public, our usage of it is open source, can be directly observed by setting LOG_LEVEL=debug before running flyctl commands, and there are no current plans to change it, be aware that this interface is not guaranteed to be stable and can change without notice. If this is a concern, consider using the fly ips command instead.

The following will create a shared IPv4 address and a dedicated IPv6 address:

Wrap textCopy to clipboard
curl -i -X POST \
  -H "Authorization: Bearer ${FLY_API_TOKEN}" \
  -H "Content-Type: application/json" \
  "https://api.fly.io/graphql" \
  -d @- <<EOF 
    {
      "query": "mutation(\$input: AllocateIPAddressInput!) { allocateIpAddress(input: \$input) { app { sharedIpAddress } } }",
      "variables": {
        "input": {
          "appId": "${APP_NAME}",
          "type": "shared_v4",
          "region": ""
        }
      }
    }
EOF

curl -i -X POST \
  -H "Authorization: Bearer ${FLY_API_TOKEN}" \
  -H "Content-Type: application/json" \
  "https://api.fly.io/graphql" \
  -d @- <<EOF 
    {
      "query": "mutation(\$input: AllocateIPAddressInput!) { allocateIpAddress(input: \$input) { ipAddress { id address type region createdAt } } }",
      "variables": {
        "input": {
          "appId": "${APP_NAME}",
          "type": "v6",
          "region": ""
        }
      }
    }
EOF
Other options include v4 and private_v6.

Create a volume
This demo uses a volume. If your application doesn’t use a volume skip this step.

Wrap textCopy to clipboard
curl -i -X POST \
  -H "Authorization: Bearer ${FLY_API_TOKEN}" \
  -H "Content-Type: application/json" \
  "${FLY_API_HOSTNAME}/v1/apps/${APP_NAME}/volumes" \
  -d '{
    "name": "data",
    "region": "iad",
    "size_gb": 1
  }'
Adjust the region as necessary.

Create a machine
This next part contains a lot of properties, so first an overview:

If you are using a volume, region selected must match a region in which you have an allocated but unattached volume.
image specifies the image we will be running. Fly.io provides an image capable of running npx and uvx, which is sufficient to run many MCPs. If you have a custom MCP with unique requirements, you can provide your own image.
init specifies the command we will be running.
guest specifies the size of the machine desired.
mounts specifies the volume, where it is to be mounted, and how it can grow.
services defined what network services your application provides.
Wrap textCopy to clipboard
curl -i -X POST \
  -H "Authorization: Bearer ${FLY_API_TOKEN}" \
  -H "Content-Type: application/json" \
  "${FLY_API_HOSTNAME}/v1/apps/${APP_NAME}/machines" \
  -d '{
    "region": "iad",
    "config": {
      "image": "flyio/mcp:latest",
      "init": {
        "cmd": [
          "npx",
          "-f",
          "@modelcontextprotocol/server-filesystem",
          "/data/"
        ]
      },
      "guest": {
        "cpu_kind": "shared",
        "cpus": 1,
        "memory_mb": 1024
      },
      "mounts": [
        {
          "volume": "data",
          "path": "/data",
          "extend_threshold_percent": 80,
          "add_size_gb": 1,
          "size_gb_limit": 100
        }
      ],
      "services": [
        {
          "protocol": "tcp",
          "internal_port": 8080,
          "autostop": "stop",
          "autostart": true,
          "ports": [
            {
              "port": 80,
              "handlers": [
                "http"
              ],
              "force_https": true
            },
            {
              "port": 443,
              "handlers": [
                "http",
                "tls"
              ]
            }
          ]
        }
      ]
    }
  }'
Note: at this time the machine is created but not yet started. It will start once it receives its first request and stop when there is a period when there are no requests.

Accessing the MCP
Normally you would access the MCP using fly mcp proxy to create a STDIO MCP server for your MCP client, even if you are using the Machines API to deploy an existing MCP server on a Fly Machine.

But for those interested in lower level details, fly mcp wrap supports the asynchronous nature of MCP servers by requiring all requests be done via HTTP POST and all replies are returned in response to a HTTP GET request. The following shell script will demonstrate that your MCP server is working:

Wrap textCopy to clipboard
curl -N https://${APP_NAME}.fly.dev/ &
process_id=$!
sleep 1
curl -i -X POST -H "Content-Type: application/json" https://${APP_NAME}.fly.dev/ -d '
{"method":"initialize","params":{"protocolVersion":"2024-11-05","capabilities":{},"clientInfo":{"name":"claude-ai","version":"0.1.0"}},"jsonrpc":"2.0","id":0}
{"jsonrpc":"2.0","method":"tools/list","id":1}
{"jsonrpc":"2.0","method":"tools/call","params":{"name":"list_directory","arguments":{"path":"/data"}},"id":2}
'
sleep 1
kill $process_id
Note that even with the sleep commands present, there is no retry logic in this script. What this means is that you may not see replies the first time you run the script, especially if your machine has not yet been started. Simply run the script again if this happens.

Performance Considerations
While the Machines API is the most performant way to create machines, there still are some considerations you need to be aware of.

Differences in performance of otherwise similar operations:
Starting a machine that is suspended is faster than starting a machine that is stopped.
Starting a machine that is stopped is faster than updating a machine.
Updating a machine is faster than creating a new machine.
There are rate limits in place.
Taken together, if you are anticipating running hundreds or even thousands of machines, it makes sense to create them over a period of time and then having them start when needed.
fly machines run
Beta documentation. This documentation has been recently released, but may still need improvements and clarifications. Please provide feedback for this documentation in our community forums or edit on github.

The Fly.io command line interface is a higher level interface that enables you to do much of what you can do via the Machines API. It is suitable for scripting and ad hoc exploration and updates.

This guide presumes that you have flyctl installed, and have successfully run either fly auth signup or fly auth login.

The first step is intended to be run in an empty directory.

Create your app
Now use the fly apps create command:

Wrap textCopy to clipboard
fly apps create --generate-name --save
If you prefer, you can replace --generate-name with a name of your choice.

You can also specify the organization by passing in a --org pparameter, or let it prompt you.

Create IP addresses for your application
The following will create a shared IPv4 address and a dedicated IPv6 address:

Wrap textCopy to clipboard
fly ips allocate-v4 --shared
fly ips allocate-v6
If your application is going to be public, but instead is only going to be accessed by other applications within your organization, run the following instead:

Wrap textCopy to clipboard
fly ips allocate-v6 --private
Create a volume
This demo uses a volume. If your application doesn’t use a volume skip this step.

Wrap textCopy to clipboard
fly volumes create data --region iad --yes
Adjust the region as necessary.

Create a machine
This next part contains a lot of flags, so first an overview:

The first parameter specifies the image we will be running. Fly.io provides an image capable of running npx and uvx, which is sufficient to run many MCPs. If you have a custom MCP with unique requirements, you can provide your own image.
The next parameter specifies the command we will be running.
--entrypoint invokes fly mcp wrap passing the command we specified.
If you are using a volume, the --region selected must match a region in which you have an allocated but unattached volume.
--volume specifies the volume, and where it is to be mounted.
The --vm-* parameters specify the size of the machine desired.
--auto* and --port define what network services your application provides.
Wrap textCopy to clipboard
fly machine run flyio/mcp:latest \
  "npx -f @modelcontextprotocol/server-filesystem /data/" \
  --entrypoint "/usr/bin/flyctl mcp wrap --" \
  --region iad --volume data:/data \
  --vm-cpu-kind shared --vm-cpus 1 --vm-memory 1024 \
  --autostart=true --autostop=stop \
  --port 80:8080/tcp:http --port 443:8080/tcp:http:tls
Note that this creates and starts a machine. If you want to only create the machine, use fly machine create instead.

Once this command completes, you can update your fly.toml to include this new information using the following command:

Wrap textCopy to clipboard
fly config save --yes
Accessing the MCP via an inspector
As the MCP inspector is a Node.js application, you need to Download and install Node.js first. MacOS users can use brew install node.

You are test out your MCP server using the MCP inspector:

Wrap textCopy to clipboard
fly mcp proxy -i
Navigate to http://127.0.0.1:6274 ; click Connect; then List Tools; select any tool; fill out the form (if any) and click Run tool.

Configure your LLM
Here’s an example claude_desktop_config.json:

Wrap textCopy to clipboard
{
  "mcpServers": {
    "filesystem": {
      "command": "/Users/rubys/.fly/bin/flyctl",
      "args": [
         "mcp",
         "proxy",
         "--url=https://mcp.fly.dev/"
       ]
    }
  }
}
Adjust the flyctl path and the value of the –url, restart your LLM (in this case, Claude) and try out the tools.
Deploy on
MCP servers can run in a variety of locations.

The Docker MCP Catalog and Toolkit announcement identifies a number of problems and potential solutions with running MCP servers on your laptop.

Running an MCP server on a Fly Machine is easy and provides an additional level of security and isolation. It can also provide access to resources that are not on your laptop such as volumes, sqlite databases, and your application’s internal state.

We recommend that you start with deploying each MCP server on a separate machine and only explore other options if you have specific needs.

A Fly Machine
Demonstrates using flyctl launch to create a Fly.io machine that runs an MCP server remotely.

A container
Demonstrates running an MCP server in a container on a fly machine

Your application
Demonstrates running an MCP server inside your application
A Fly Machine
Beta documentation. This documentation has been recently released, but may still need improvements and clarifications. Please provide feedback for this documentation in our community forums or edit on github.

Fly Machines are fast-launching VMs; they can be started and stopped at subsecond speeds. We give you control of your Machine count and each Machine’s lifecycle, resources, and region placement with a simple REST API or flyctl commands.

This guide presumes that you have flyctl installed, and have successfully run either fly auth signup or fly auth login.

The first step is intended to be run in an empty directory.

Create your app
Create a Dockerfile with the following contents:

Wrap textCopy to clipboard
FROM flyio/mcp
VOLUME /data
CMD [ "npx", "-f", "@modelcontextprotocol/server-filesystem", "/data/" ]
Now use the fly launch command:

Wrap textCopy to clipboard
fly launch
Review and accept the defaults.

The Dockerfile will be build, and the resulting image will be pushed and deployed. In the process, a volume will be allocated and both a shared ipv4 and a dedicated ipv6 address will be allocated.

Accessing the MCP via an inspector
As the MCP inspector is a Node.js application, you need to Download and install Node.js first. MacOS users can use brew install node.

You are test out your MCP server using the MCP inspector:

Wrap textCopy to clipboard
fly mcp proxy -i
Navigate to http://127.0.0.1:6274 ; click Connect; then List Tools; select any tool; fill out the form (if any) and click Run tool.

Configure your LLM
Here’s an example claude_desktop_config.json:

Wrap textCopy to clipboard
{
  "mcpServers": {
    "filesystem": {
      "command": "/Users/rubys/.fly/bin/flyctl",
      "args": [
         "mcp",
         "proxy",
         "--url=https://mcp.fly.dev/"
       ]
    }
  }
}
Adjust the flyctl path and the value of the –url, restart your LLM (in this case, Claude) and try out the tools.
HTTP Authorization
Beta documentation. This documentation has been recently released, but may still need improvements and clarifications. Please provide feedback for this documentation in our community forums or edit on github.

The HTTP Streaming transport specifies OAuth 2.1 for authentication. To work this needs to be implemented in both the MCP client and the MCP server. As of Spring 2025, this is not yet widely implemented.

The SSE transport only specified Implement proper authentication for all SSE connections. As again this needs to be implemented in both the MCP client and MCP server to work, this guidance is not sufficient for interoperability. THe MCP inspector lets you set a bearer token, and there are some who followed this lead. That being said, the SSE transport is now deprecated.

For stdio transports, there is no authentication; that is left entirely up to fly mcp proxy and fly mcp wrap. As these commands are designed to be used with an MCP server that was only intended to be used by a single user at a time, OAuth is substantial overkill for this purpose. Instead these commands support both basic and bearer HTTP Authorization.

To use basic authentication, set two secrets in your application. For example:

Wrap textCopy to clipboard
fly secrets set FLY_MCP_USER=Admin FLY_MCP_PASSWORD=S3cr3t
To use bearer authentication, set one secret in your application. For example:

Wrap textCopy to clipboard
fly secrets set FLY_MCP_BEARER_TOKEN=T0k3n
If you are using MacOs, Linux, or WSL2, the following command may be useful for generating a token:

Wrap textCopy to clipboard
openssl rand -base64 18
And then on the client side pass the same values to the proxy as flags:

For basic:

Wrap textCopy to clipboard
{
  "mcpServers": {
    "filesystem": {
      "command": "/Users/rubys/.fly/bin/flyctl",
      "args": [
         "mcp",
         "proxy",
         "--url=https://mcp.fly.dev/",
         "--user",
         "Admin",
         "--password",
         "S3cr3t"
       ]
    }
  }
}
For bearer:

Wrap textCopy to clipboard
{
  "mcpServers": {
    "filesystem": {
      "command": "/Users/rubys/.fly/bin/flyctl",
      "args": [
         "mcp",
         "proxy",
         "--url=https://mcp.fly.dev/",
         "--bearer-token",
         "T0k3n"
       ]
    }
  }
}
From a security point of view, there is not a substantial difference between these two authentication methods. Pick the one you fine most convenient.
Wireguard tunnels and Flycast
Beta documentation. This documentation has been recently released, but may still need improvements and clarifications. Please provide feedback for this documentation in our community forums or edit on github.

The best way not to let randos on the internet access to your MCP server is to not put the MCP server on the internet in the first place.

Every Fly Organization has a private network. In most cases, you will want only a private v6 address on applications that are not available on the internet.

When using:

The Machine API, specify private_v6.
fly ips, specify allocate-v6 --private
fly launch, specify --flycast
With this in place you can use fly proxy to create a tunnel, or you can follow our blueprint to Jack into your private network with WireGuard.

With fly mcp proxy, this support is built in. To use, simply specify a --url ending in .internal or .flycast.

.internal addresses can be used to target individual machines or regions, but can only be used to access machines that are started. Just remember that the protocol to use is http not https, and the port you want to use it the internal port. So an typical URL would look like http://mcp.internal:8080/.
.flycast addresses target an external port for your application, and supports fly routing headers. If your request is routed to a machine that is stopped or suspended, that machine will be started first. Again the protocol to use is http not https, so an typical URL would look like http://mcp.flycast/.
Flycast - Private Fly Proxy services provides more information on the use of Flycast.

fly mcp wrap has a --private flag which will cause the proxy to respond with a 403 Forbidden response to all requests that do not come in via the private network. This may be useful when combined with containers and machines with multiple services, some of which are public but the MCP server is private.
flyctl mcp server
Scotty talking to a computer

Adding fly mcp server to your LLM
Wrap textCopy to clipboard
fly mcp server --claude
You can also specify --cursor, --neovim, --vscode, --windsurf, or --zed. Or specify a configuration file path directly using --config.

flyctl provides an MCP server that you can use to provision your application. At the present time, most of the following commands and their subcommands are supported:

apps - Manage Fly applications. A Fly App is an abstraction for a group of Fly Machines running your code on Fly.io.
certs - Manage the certificates associated with a deployed application.
logs - View application logs as generated by the application running on the Fly platform.
machine - Manage Fly Machines. Fly Machines are super-fast, lightweight VMs that can be created, and then quickly started and stopped as needed with flyctl commands or with the Machines REST fly.
orgs - Manage Fly organizations. Organization admins can also invite or remove users from organizations.
platform - Information about the Fly platform
secrets - Manage secrets. Secrets are provided to applications at runtime as ENV variables.
status - Show the application’s current status including application details, tasks, most recent deployment details and in which regions it is currently allocated.
volumes - Manage Fly Volumes. Volumes are persistent storage for Fly Machines.
Running with the MCP inspector
You can explore the flyctl mcp server using the MCP inspector:

As the MCP inspector is a Node.js application, you need to Download and install Node.js first. MacOS users can use brew install node.

Wrap textCopy to clipboard
fly mcp server -i
Navigate to http://127.0.0.1:6274 ; click Connect; then List Tools; then a tool like fly-platform-status, fly-orgs-list, fly-apps-list, or fly-machines-list; then fill out the form (if any) and click Run tool.

Running on a separate machine
Running this server remotely can give others access to run commands on your behalf. Read the following carefully before proceeding.

Both --sse and -stream options are supported.

The default bind address is 127.0.0.1 which will only allow requests from the same machine. to override specify --bind-addr.

Authentication tokens come from (in priority order):

bearer-token from the Authentication header on the request
--access-token flag on the fly mcp server command
FLY_ACCESS_TOKEN environment variable
See Access Tokens for information on how to obtain a token.

Report an issue
or
edit this page on GitHub
Examples
While MCPs and Fly.io have a lot of concepts, when launching MCPs on Fly.io you generally only have to worry about:

Host tool (examples: Claude, Cursor, Neovim, VSCode, Windsurf, Zed)
MCP server name. If you are using, for example, Claude as your host and connect multiple MCP servers to it, you need to give each MCP server a name.
Secrets. If you see places in the docs where they tell you to put secrets in environment variables, you will instead put them in secrets. Your MCP servers will be able to access these secrets, but your host tool will not.
That’s it. You don’t have to worry about streaming, authentication, fly.toml.

Try some of the following commands. After running them, restart Claude and ask it what tools it has access to.

flyctl server
We provide a flyctl MCP server for issuing flyctl commands:

Wrap textCopy to clipboard
fly mcp server --claude --server flyctl
Fetch
Run Fetch MCP server where it doesn’t have access to your local servers:

Wrap textCopy to clipboard
fly mcp launch "uvx mcp-server-fetch" --claude --server fetch
Fly.io internal DNS
mcp-internal-dns enables your MCP client to query Fly.io .internal DNS:

Wrap textCopy to clipboard
fly mcp launch "npx -y @flydotio/mcp-internal-dns" --claude --server dns
Slack
Look at the Slack setup instructions and obtain a Bot User OAuth Token and Team ID, then run:

Wrap textCopy to clipboard
fly mcp launch \
  "npx -y @modelcontextprotocol/server-slack" \
  --claude --server slack \
  --secret SLACK_BOT_TOKEN=xoxb-your-bot-token \
  --secret SLACK_TEAM_ID=T01234567
Filesystem / volume
The Filesystem MCP can be paired with a Fly.io volume:

Wrap textCopy to clipboard
fly mcp launch "npx -y @modelcontextprotocol/server-filesystem /data/" \
  --claude --server volume --volume data:/data:initial_size=1GB
You can do the same thing with the go mcp-filesystem-server:

Wrap textCopy to clipboard
fly mcp launch "go run github.com/mark3labs/mcp-filesystem-server@latest /data/" \
  --claude --server volume --volume data:/data:initial_size=1GB
GitHub
If you have the Github CLI installed, you can launch the GitHub MCP Server:

Wrap textCopy to clipboard
flyctl mcp launch --image ghcr.io/github/github-mcp-server \
  --secret GITHUB_PERSONAL_ACCESS_TOKEN=$(gh auth token) \
  --claude --server github --name git
Desktop Commander
You can run DesktopCommander which requires a setup step:

Wrap textCopy to clipboard
fly mcp launch "npx @wonderwhy-er/desktop-commander@latest" \
  --claude --server desktop-commander \
  --setup "RUN npx -y @wonderwhy-er/desktop-commander@latest setup"