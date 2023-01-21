"""
comics/constants
~~~~~~~~~~~~~~~~
"""

from . import api

# fmt: off
COMICS_CLASS = (
    api.a_problem_like_jamal, api.aaggghhh, api.adam_at_home, api.adult_children, api.agnes,
    api.aj_and_magnus, api.al_goodwyn_editorial_cartoons, api.alis_house, api.alley_oop, api.amanda_the_great,
    api.andertoons, api.andy_capp, api.angry_little_girls, api.animal_crackers, api.annie, api.arlo_and_janis,
    api.art_by_moga, api.ask_shagg, api.at_tavicat, api.aunty_acid, api.baby_blues, api.back_in_the_day,
    api.back_to_bc, api.bacon, api.bad_machinery, api.baldo, api.baldo_en_espanol, api.ballard_street, api.banana_triangle,
    api.barkeater_lake, api.barney_and_clyde, api.basic_instructions, api.batch_rejection, api.bc, api.beanie_the_brownie,
    api.bear_with_me, api.beardo, api.ben, api.benitin_y_eneas, api.berger_and_wyse, api.berkeley_mews, api.betty,
    api.bfgf_syndrome, api.big_nate, api.big_nate_first_class, api.big_top, api.bird_and_moon, api.birdbrains,
    api.bleeker_the_rechargeable_dog, api.bliss, api.bloom_county, api.bloom_county_2019, api.bo_nanas, api.bob_gorrell,
    api.bob_the_squirrel, api.boomerangs, api.bottom_liners, api.bound_and_gagged, api.bozo, api.break_of_day,
    api.breaking_cat_news, api.brevity, api.brewster_rockit, api.brian_mcfadden, api.broom_hilda, api.buckles, api.bully,
    api.buni, api.calvin_and_hobbes, api.calvin_and_hobbes_en_espanol, api.candorville, api.catana_comics, api.cathy,
    api.cathy_commiserations, api.cats_cafe, api.cattitude_doggonit, api.cest_la_vie, api.cheer_up_emo_kid, api.chip_bok,
    api.chris_britt, api.chuck_draws_things, api.chuckle_bros, api.citizen_dog, api.claw, api.clay_bennett, api.clay_jones,
    api.cleats, api.close_to_home, api.compu_toon, api.cornered, api.cow_and_boy, api.cowtown, api.crabgrass, api.crumb,
    api.cul_de_sac, api.daddys_home, api.dana_summers, api.dark_side_of_the_horse, api.deep_dark_fears,
    api.deflocked, api.diamond_lil, api.dick_tracy, api.dilbert, api.dilbert_en_espanol, api.dinosaur_comics, api.dog_eat_doug,
    api.dogs_of_c_kennel, api.domestic_abuse, api.don_brutus, api.doodle_for_food, api.doodle_town, api.doonesbury, api.drabble,
    api.drew_sheneman, api.dumbwich_castle, api.edge_city, api.eek, api.el_café_de_poncho, api.emmy_lou, api.endtown,
    api.eric_allie, api.everyday_people_cartoons, api.eyebeam, api.eyebeam_classic, api.f_minus, api.false_knees,
    api.family_tree, api.farcus, api.fat_cats, api.flo_and_friends, api.foolish_mortals, api.for_better_or_for_worse,
    api.for_heavens_sake, api.four_eyes, api.fowl_language, api.foxtrot, api.foxtrot_classics, api.foxtrot_en_espanol,
    api.francis, api.frank_and_ernest, api.frazz, api.fred_basset, api.fred_basset_en_espanol, api.free_range,
    api.freshly_squeezed, api.frog_applause, api.g_man_webcomics, api.garfield, api.garfield_classics, api.garfield_en_espanol,
    api.gary_markstein, api.gary_varvel, api.gasoline_alley, api.gaturro, api.geech, api.get_a_life, api.get_fuzzy, api.gil,
    api.gil_thorp, api.ginger_meggs, api.ginger_meggs_en_espanol, api.glasbergen_cartoons, api.globetrotter, api.goats,
    api.grand_avenue, api.gray_matters, api.green_humour, api.haircut_practice, api.half_full, api.harley, api.heart_of_the_city,
    api.heathcliff, api.heathcliff_en_espanol, api.henry_payne, api.herb_and_jamaal, api.herman, api.home_and_away, api.home_free,
    api.hot_comics_for_cool_people, api.hutch_owen, api.imagine_this, api.imogen_quest, api.in_security, api.in_the_bleachers,
    api.in_the_sticks, api.ink_pen, api.invisible_bread, api.its_all_about_you, api.jack_ohman, api.jake_likes_onions,
    api.janes_world, api.jeff_danziger, api.jeff_stahler, api.jen_sorensen, api.jerry_king_comics, api.jim_benton_cartoons,
    api.jim_morin, api.joe_heller, api.joel_pett, api.john_deering, api.jumpstart, api.junk_drawer, api.justo_y_franco,
    api.kevin_kallaugher, api.kevin_necessary_editorial_cartoons, api.kid_beowulf, api.kitchen_capers, api.kliban, api.klibans_cats,
    api.la_cucaracha, api.la_cucaracha_en_espanol, api.lalo_alcaraz, api.lalo_alcaraz_en_espanol, api.lards_world_peace_tips,
    api.las_hermanas_stone, api.last_kiss, api.laughing_redhead_comics, api.lay_lines, api.learn_to_speak_cat, api.liberty_meadows,
    api.life_on_earth, api.lil_abner, api.lio, api.lio_en_espanol, api.lisa_benson, api.little_dog_lost,
    api.little_fried_chicken_and_sushi, api.little_nemo, api.liz_climo_cartoons, api.lola, api.lola_en_espanol, api.long_story_short,
    api.looks_good_on_paper, api.loose_parts, api.los_osorios, api.lost_sheep, api.luann, api.luann_againn, api.luann_en_espanol,
    api.lucky_cow, api.lug_nuts, api.lunarbaboon, api.m2bulls, api.maintaining, api.mannequin_on_the_moon, api.marias_day,
    api.marmaduke, api.marshall_ramsey, api.matt_bors, api.matt_davies, api.matt_wuerker, api.medium_large, api.messycow_comics,
    api.mexikid_stories, api.michael_ramirez, api.mike_beckom, api.mike_du_jour, api.mike_lester, api.mike_luckovich, api.miss_peach,
    api.moderately_confused, api.momma, api.monty, api.monty_diaros, api.motley, api.mr_lowe, api.mt_pleasant, api.mutt_and_jeff,
    api.my_dad_is_dracula, api.mythtickle, api.nancy, api.nancy_classics, api.nate_el_grande, api.nest_heads, api.neurotica,
    api.new_adventures_of_queen_victoria, api.next_door_neighbors, api.nick_and_zuzu, api.nick_anderson, api.nine_chickweed_lane,
    api.nine_chickweed_lane_classics, api.nine_to_five, api.non_sequitur, api.not_invented_here, api.nothing_is_not_something,
    api.now_recharging, api.off_the_mark, api.oh_brother, api.ollie_and_quentin, api.on_a_claire_day, api.one_and_done, api.one_big_happy,
    api.ordinary_bill, api.origins_of_the_sunday_comics, api.our_super_adventure, api.out_of_the_gene_pool_re_runs, api.outland,
    api.over_the_hedge, api.overboard, api.overboard_en_espanol, api.ozy_and_millie, api.pat_oliphant, api.pc_and_pixel, api.peanuts,
    api.peanuts_begins, api.pearls_before_swine, api.pedro_x_molina, api.periquita, api.perlas_para_los_cerdos, api.perry_bible_fellowship,
    api.petunia_and_dre, api.phil_hands, api.phoebe_and_her_unicorn, api.pibgorn, api.pibgorn_sketches, api.pickles, api.please_listen_to_me,
    api.pluggers, api.pooch_cafe, api.poorcraft, api.poorly_drawn_lines, api.pot_shots, api.preteena, api.prickly_city,
    api.questionable_quotebook, api.rabbits_against_magic, api.raising_duncan, api.randolph_itch_2_am, api.real_life_adventures,
    api.reality_check, api.rebecca_hendin, api.red_and_rover, api.red_meat, api.richards_poor_almanac, api.rip_haywire,
    api.ripleys_aunque_usted_no_lo_crea, api.ripleys_believe_it_or_not, api.rob_rogers, api.robbie_and_bobby, api.robert_ariail,
    api.rose_is_rose, api.rosebuds, api.rosebuds_en_espanol, api.rubes, api.rudy_park, api.salt_n_pepper, api.sarahs_scribbles,
    api.saturday_morning_breakfast_cereal, api.savage_chickens, api.scary_gary, api.scenes_from_a_multiverse, api.scott_stantis,
    api.shen_comix, api.shermans_lagoon, api.shirley_and_son, api.shoe, api.signe_wilkinson, api.sketchshark_comics, api.skin_horse,
    api.skippy, api.small_potatoes, api.snoopy_en_espanol, api.snow_sez, api.snowflakes, api.speed_bump, api.spirit_of_the_staircase,
    api.spot_the_frog, api.steve_benson, api.steve_breen, api.steve_kelley, api.sticky_comics, api.stone_soup, api.stone_soup_classics,
    api.strange_brew, api.stuart_carlson, api.studio_jantze, api.sunny_street, api.sunshine_state, api.super_fun_pak_comix,
    api.swan_eaters, api.sweet_and_sour_pork, api.sylvia, api.tank_mcnamara, api.tarzan, api.tarzán_en_espanol, api.ted_rall, api.ten_cats,
    api.tex, api.texts_from_mittens, api.that_is_priceless, api.that_new_carl_smell, api.thatababy, api.the_academia_waltz,
    api.the_adventures_of_business_cat, api.the_argyle_sweater, api.the_awkward_yeti, api.the_barn, api.the_big_picture, api.the_boondocks,
    api.the_born_loser, api.the_buckets, api.the_city, api.the_comic_strip_that_has_a_finale_every_day, api.the_daily_drawing,
    api.the_dinette_set, api.the_doozies, api.the_duplex, api.the_elderberries, api.the_flying_mccoys, api.the_fusco_brothers,
    api.the_grizzwells, api.the_humble_stumble, api.the_k_chronicles, api.the_knight_life, api.the_martian_confederacy,
    api.the_meaning_of_lila, api.the_middle_age, api.the_middletons, api.the_norm, api.the_other_coast,
    api.the_upside_down_world_of_gustave_verbeek, api.the_wandering_melon, api.the_wizard_of_id_spanish, api.the_worried_well,
    api.thin_lines, api.think, api.tim_campbell, api.tiny_sepuku, api.todays_szep, api.tom_the_dancing_bug, api.tom_toles,
    api.too_much_coffee_man, api.trucutu, api.truth_facts, api.tutelandia, api.two_party_opera, api.underpants_and_overbites,
    api.understanding_chaos, api.unstrange_phenomena, api.views_of_the_world, api.viewsafrica, api.viewsamerica, api.viewsasia,
    api.viewsbusiness, api.viewseurope, api.viewslatinamerica, api.viewsmideast, api.viivi_and_wagner, api.w_t_duck, api.wallace_the_brave,
    api.walt_handelsman, api.warped, api.watch_your_head, api.wawawiwa, api.waynovision, api.wee_pals, api.widdershins, api.wide_open,
    api.win_lose_drew, api.wizard_of_id, api.wizard_of_id_classics, api.wondermark, api.working_daze, api.working_it_out, api.worry_lines,
    api.wrong_hands, api.wumo, api.wumo_en_espanol, api.yaffle, api.yes_im_hot_in_this, api.zack_hill, api.zen_pencils, api.ziggy, api.ziggy_en_espanol,
)
# fmt: on


class directory:
    """Directory of registered comics in GoComics."""

    _registered_comics = {cls_.title.lower(): cls_.__name__ for cls_ in COMICS_CLASS}

    @classmethod
    def listall(cls):
        """Returns every registered comic in GoComics.

        Returns:
            tuple: Every registered comic in GoComics.
        """
        return tuple(sorted(cls._registered_comics.values()))

    @classmethod
    def search(cls, key):
        """Searches directory of registered comics in GoComics for keyword.

        Args:
            key (str): Keyword to search directory for comic.

        Returns:
            tuple: Every registered comic in GoComics containing the queried keyword.
        """
        return tuple(
            cls_name
            for title, cls_name in cls._registered_comics.items()
            if key.lower() in title.lower()
        )
