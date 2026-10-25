import java.awt.*; import java.awt.geom.*; import java.awt.image.*; import javax.imageio.*; import java.io.*;
public class Icon { public static void main(String[] a) throws Exception {
  String root=a[0]; int[] sz={48,72,96,144,192}; String[] d={"mdpi","hdpi","xhdpi","xxhdpi","xxxhdpi"};
  for(int i=0;i<sz.length;i++){ int s=sz[i]; BufferedImage im=new BufferedImage(s,s,BufferedImage.TYPE_INT_ARGB);
    Graphics2D g=im.createGraphics(); g.setRenderingHint(RenderingHints.KEY_ANTIALIASING,RenderingHints.VALUE_ANTIALIAS_ON); g.setRenderingHint(RenderingHints.KEY_TEXT_ANTIALIASING,RenderingHints.VALUE_TEXT_ANTIALIAS_ON);
    float m=s*0.04f; g.setPaint(new GradientPaint(0,0,new Color(0xE11D48),s,s,new Color(0x7C3AED)));
    g.fill(new RoundRectangle2D.Float(m,m,s-2*m,s-2*m,s*0.3f,s*0.3f));
    g.setColor(Color.WHITE); g.setFont(new Font("SansSerif",Font.BOLD,(int)(s*0.42)));
    FontMetrics fm=g.getFontMetrics(); String t="EA"; g.drawString(t,(s-fm.stringWidth(t))/2f,(s-fm.getHeight())/2f+fm.getAscent());
    g.dispose(); File f=new File(root+"/mipmap-"+d[i]+"/ic_launcher.png"); f.getParentFile().mkdirs(); ImageIO.write(im,"png",f);} } }
