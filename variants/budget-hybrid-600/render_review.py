"""Render the two quoted scope levels from the generated assembly geometry."""
from PIL import Image,ImageDraw
from build_candidate import OUT,pieces,bolted_datums
from motion_context import motion_parts
from preview import render,font

def main():
    fixed,_,wet=pieces()
    stand=[p for p in fixed if p[0].startswith(('L_motion','R_motion','L_steel','R_steel','L_column','R_column','L_wall','R_wall','end_X','bearer_','center_post','foot_','L_end_bearing','R_end_bearing','pan_4040','pan_slot_tab'))]
    panels=[(stand,False,'01   Braced stand','$561.17 delivered materials'),(fixed+wet+bolted_datums(motion_parts(True)),True,'02   Reinforced hybrid','$1,601.54 delivered table materials')]
    canvas=Image.new('RGB',(1340,655),'#f6f7f6');pen=ImageDraw.Draw(canvas)
    pen.text((42,22),'Nine-foot carving and plasma table',font=font(34,True),fill='#183449')
    pen.text((45,75),'Nine adjustable feet  /  Motion shown for fit and excluded from both prices',font=font(19),fill='#536872')
    for i,(parts,back,label,price) in enumerate(panels):
        x=44+i*650
        im=render(parts,back,w=840,h=605);im.thumbnail((605,421),Image.Resampling.LANCZOS)
        canvas.paste(im,(x+(605-im.width)//2,118+(421-im.height)//2))
        pen.text((x,554),label,font=font(24,True),fill='#183449')
        pen.text((x,594),price,font=font(19),fill='#14645F')
    canvas.save(OUT/'scope-preview.png')
if __name__=='__main__':main()
