"""Pull FIRST LIGHT's playable skyline toward the promise of its title screen.

This is a restrained silhouette pass, not blanket prop clutter. Existing original Aegis
Reach architecture is reused as non-colliding distant/edge massing around Northstar:
a broken orbital-array crown, cyan-accented signal spires, bunker silhouettes and
retaining masses. Gameplay routes, combat cover and the landing zone remain owned by
the existing mission builders.
"""

CROWN = r'Aegis Reach\Orbital Antenna Arc.fpe'
SPIRE = r'Aegis Reach\Signal Spire.fpe'
BUNKER = r'Aegis Reach\Relay Bunker.fpe'
BASTION = r'Aegis Reach\Bastion Wall.fpe'
DECK = r'Aegis Reach\Station Deck.fpe'

# name, asset, x, z, scale, yaw, height offset, kind
LANDMARKS = (
    # Hero broken-array silhouette behind Northstar, echoing the title art without
    # putting collision or a giant prop into the traversal lane.
    ('TITLE // NORTHSTAR CROWN ARRAY', CROWN, -250, 1250, 315, 18, -55, 'title_landmark'),
    ('TITLE // NORTHSTAR CROWN ARRAY AFT', CROWN, 380, 1510, 245, 198, -70, 'title_landmark'),

    # A readable relay-spire hierarchy. These use the project's original cyan-accent
    # atlas and provide vertical rhythm from Camp 12 through the Northstar approach.
    ('TITLE // NORTHSTAR RELAY SPIRE 01', SPIRE, -2140, -250, 205, 0, -12, 'title_spire'),
    ('TITLE // NORTHSTAR RELAY SPIRE 02', SPIRE, -980, 460, 235, 8, -18, 'title_spire'),
    ('TITLE // NORTHSTAR RELAY SPIRE 03', SPIRE, 420, 520, 190, -10, -16, 'title_spire'),
    ('TITLE // OPERATIONS RELAY SPIRE 04', SPIRE, 2050, 720, 170, 12, -10, 'title_spire'),
    ('TITLE // AEGIS RELAY SPIRE 05', SPIRE, 920, 2700, 220, -12, -24, 'title_spire'),

    # Fortified massing stays outside the authored combat lanes. Physics is disabled;
    # these pieces are composition and scale cues only.
    ('TITLE // NORTHSTAR BUNKER MASS 01', BUNKER, -2500, -620, 135, 12, -18, 'title_mass'),
    ('TITLE // NORTHSTAR BUNKER MASS 02', BUNKER, -2440, 360, 125, 168, -18, 'title_mass'),
    ('TITLE // OPERATIONS BUNKER MASS 03', BUNKER, 2360, 520, 125, 255, -14, 'title_mass'),
    ('TITLE // NORTHSTAR RETAINING 01', BASTION, -2550, 780, 145, 92, -28, 'title_mass'),
    ('TITLE // NORTHSTAR RETAINING 02', BASTION, 2320, 1480, 135, 268, -26, 'title_mass'),
    ('TITLE // NORTHSTAR INDUSTRIAL DECK', DECK, -520, 650, 72, 6, -34, 'title_mass'),
)


def apply(build):
    placed=[]
    for name,asset,x,z,scale,yaw,yoff,kind in LANDMARKS:
        y=build.ground(x,z)+yoff
        build.add(asset,name,x,z,y=y,ry=yaw,scale=scale,kind=kind,
                  **{'eleprof.physics':0,'eleprof.phyalways':0,'eleprof.isimmobile':1})
        placed.append({'name':name,'asset':asset,'x':x,'z':z,'scale':scale,'kind':kind})
    return {
        'title_screen_target':'cold fortified Northstar skyline with broken crown array, relay spires and layered industrial massing',
        'entity_count':len(placed),
        'crown_count':sum(1 for p in placed if 'CROWN ARRAY' in p['name']),
        'spire_count':sum(1 for p in placed if p['kind']=='title_spire'),
        'mass_count':sum(1 for p in placed if p['kind']=='title_mass'),
        'gameplay_collision':False,
        'placements':placed,
    }
