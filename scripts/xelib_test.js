async function main() {
  let files = [
    'Fallout4.esm',
    'DLCRobot.esm',
    'DLCWorkshop01.esm',
    'DLCCoast.esm',
    'DLCWorkshop02.esm',
    'DLCWorkshop03.esm',
    'DLCNukaWorld.esm',
    'LondonWorldSpace.esm',
  ];

  let xelib = require('xelib').wrapper;
  xelib.Initialize('XEditLib.dll');
  xelib.SetGameMode(xelib.gmFO4);

  console.time('loading');

  xelib.LoadPlugins(files.join('\n'));

  while(true) {
    let status = xelib.GetLoaderStatus();
    if (status == xelib.lsDone) {
      console.log('All OK');
      break;
    }

    if (status == xelib.lsError ) {
      console.log.error('CRITICAL ERROR: Loading plugins/resources failed!');
      break;
    }

    await new Promise(resolve => setTimeout(resolve, 200));

    let str = xelib.GetMessages();
    if (str.length > 1) {
    let messages = str.slice(0, -2).split('\n');
      const clip = (s,w)=>s;//.slice(w)+' '.repeat(Math.max(0,w-s.length))
      messages.forEach(s=>process.stdout.write(`${clip(s,80)}\r`));
    }

  }

  console.timeEnd('loading');
}

main()
