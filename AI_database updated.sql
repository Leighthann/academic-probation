PGDMP                      }         	   AIproject    17.4    17.4                0    0    ENCODING    ENCODING        SET client_encoding = 'UTF8';
                           false                       0    0 
   STDSTRINGS 
   STDSTRINGS     (   SET standard_conforming_strings = 'on';
                           false                       0    0 
   SEARCHPATH 
   SEARCHPATH     8   SELECT pg_catalog.set_config('search_path', '', false);
                           false                       1262    16387 	   AIproject    DATABASE     q   CREATE DATABASE "AIproject" WITH TEMPLATE = template0 ENCODING = 'UTF8' LOCALE_PROVIDER = libc LOCALE = 'en-US';
    DROP DATABASE "AIproject";
                     postgres    false            �            1259    24606    admin_master    TABLE     o   CREATE TABLE public.admin_master (
    "Admin ID" text NOT NULL,
    "Admin Name" text,
    "Password" text
);
     DROP TABLE public.admin_master;
       public         heap r       postgres    false            �            1259    24620    advisors    TABLE     ^   CREATE TABLE public.advisors (
    "Student ID" text NOT NULL,
    "Academic Advisor" text
);
    DROP TABLE public.advisors;
       public         heap r       postgres    false            �            1259    24627    module_details    TABLE     �   CREATE TABLE public.module_details (
    "Module Code" text,
    "module name" text,
    semester integer,
    "Student ID" text,
    "Grade point" double precision,
    "Year" text
);
 "   DROP TABLE public.module_details;
       public         heap r       postgres    false            �            1259    16393    module_master    TABLE     �   CREATE TABLE public.module_master (
    "Module Code" text NOT NULL,
    "Module" text NOT NULL,
    "Number of Credits" integer NOT NULL
);
 !   DROP TABLE public.module_master;
       public         heap r       postgres    false            �            1259    24613    sign_in    TABLE     g   CREATE TABLE public.sign_in (
    "ID Num" text NOT NULL,
    "Password" text,
    "Status" boolean
);
    DROP TABLE public.sign_in;
       public         heap r       postgres    false            �            1259    16398    student_master    TABLE     �   CREATE TABLE public.student_master (
    "Student ID" text NOT NULL,
    "Student Name" text NOT NULL,
    "Student Email" text NOT NULL,
    "School" text NOT NULL,
    "Programme" text NOT NULL,
    "Password" text NOT NULL
);
 "   DROP TABLE public.student_master;
       public         heap r       postgres    false            �            1259    24599    teacher_master    TABLE     �   CREATE TABLE public.teacher_master (
    "Teacher ID" text NOT NULL,
    "Teacher Name" text,
    email text,
    "Position" text,
    programme text
);
 "   DROP TABLE public.teacher_master;
       public         heap r       postgres    false                      0    24606    admin_master 
   TABLE DATA           L   COPY public.admin_master ("Admin ID", "Admin Name", "Password") FROM stdin;
    public               postgres    false    220   �                 0    24620    advisors 
   TABLE DATA           D   COPY public.advisors ("Student ID", "Academic Advisor") FROM stdin;
    public               postgres    false    222   �                 0    24627    module_details 
   TABLE DATA           u   COPY public.module_details ("Module Code", "module name", semester, "Student ID", "Grade point", "Year") FROM stdin;
    public               postgres    false    223   '                 0    16393    module_master 
   TABLE DATA           U   COPY public.module_master ("Module Code", "Module", "Number of Credits") FROM stdin;
    public               postgres    false    217   �                 0    24613    sign_in 
   TABLE DATA           A   COPY public.sign_in ("ID Num", "Password", "Status") FROM stdin;
    public               postgres    false    221   v                 0    16398    student_master 
   TABLE DATA           z   COPY public.student_master ("Student ID", "Student Name", "Student Email", "School", "Programme", "Password") FROM stdin;
    public               postgres    false    218   �                 0    24599    teacher_master 
   TABLE DATA           d   COPY public.teacher_master ("Teacher ID", "Teacher Name", email, "Position", programme) FROM stdin;
    public               postgres    false    219   �       v           2606    24612    admin_master admin_master_pkey 
   CONSTRAINT     d   ALTER TABLE ONLY public.admin_master
    ADD CONSTRAINT admin_master_pkey PRIMARY KEY ("Admin ID");
 H   ALTER TABLE ONLY public.admin_master DROP CONSTRAINT admin_master_pkey;
       public                 postgres    false    220            z           2606    24626    advisors advisors_pkey 
   CONSTRAINT     ^   ALTER TABLE ONLY public.advisors
    ADD CONSTRAINT advisors_pkey PRIMARY KEY ("Student ID");
 @   ALTER TABLE ONLY public.advisors DROP CONSTRAINT advisors_pkey;
       public                 postgres    false    222            p           2606    16406     module_master module_master_pkey 
   CONSTRAINT     i   ALTER TABLE ONLY public.module_master
    ADD CONSTRAINT module_master_pkey PRIMARY KEY ("Module Code");
 J   ALTER TABLE ONLY public.module_master DROP CONSTRAINT module_master_pkey;
       public                 postgres    false    217            x           2606    24619    sign_in sign_in_pkey 
   CONSTRAINT     X   ALTER TABLE ONLY public.sign_in
    ADD CONSTRAINT sign_in_pkey PRIMARY KEY ("ID Num");
 >   ALTER TABLE ONLY public.sign_in DROP CONSTRAINT sign_in_pkey;
       public                 postgres    false    221            r           2606    16408 "   student_master student_master_pkey 
   CONSTRAINT     j   ALTER TABLE ONLY public.student_master
    ADD CONSTRAINT student_master_pkey PRIMARY KEY ("Student ID");
 L   ALTER TABLE ONLY public.student_master DROP CONSTRAINT student_master_pkey;
       public                 postgres    false    218            t           2606    24605 "   teacher_master teacher_master_pkey 
   CONSTRAINT     j   ALTER TABLE ONLY public.teacher_master
    ADD CONSTRAINT teacher_master_pkey PRIMARY KEY ("Teacher ID");
 L   ALTER TABLE ONLY public.teacher_master DROP CONSTRAINT teacher_master_pkey;
       public                 postgres    false    219               C   x�3426153�N,K��K�P����)�LL���3�q����rz�g&'*�g I��qqq ��4         @   x�Mʹ�0��H��p/�_G�	��j���B,#�N�rݙ\&U��F"d?���sp�y�         ^  x���Qo�0��˯�/`�m��H��H�f��^��X�	�p��~�����z�9�,�% �Kn�4�2-
�,H��}�3�(���>o�� �Z/��*GH�2�0s�4��\��Zi���� C�(Jpxީ��@�����,��Be�]�iv�V(#�El�uC���޵.*l�8�{S^]��|
���%��t�Pn�2�ǡ�ƅM��� q��G�h{��ٳM�C�y�5q�g<]!�A�����]]A�s���S�¸'虑��K!�A�6nw�4�㽞-��qz��m��o��ѲQ���d�Tv���#a6:Z�U]H]�9Nj������<����         �   x�MNKj�0]�O1'(ېviLBukP��l{�,�Hr���e�����;W�$8��N*jg�v��y���[�lTE���Zg~�����,���U/�٣휥ZT��f����3���ږ�g�^�;�uc�e�w�WƤ������F����5n���SVB�����Q-(c����R�7_�_oR�wI��`�o!�_^���n�W	         t   x�U�K�0�u|d�vwa��Ԩ|$`��Ta��<�EM�1�JXR�HF*�}{لDFc��ӗ�R����_MD�A+~N�֘�z�ܞ�υ�P���~� ���'b         �   x���AN�0����>Ad�IMw��E%*P�Ć�$XɈx���c{�8���ͨ�l�Q�[&G�A$����p%�.c=:����������a$Ϡ*�)��MQii���"��؆�X�wo�H<~Y!�٪�2)���Ż��fKJUo�p�}��N�o����:p�Gbk��Ę�+c��
n��jc��d��r��oWndm�H(��S�������eQ�#<��         �   x���Mj�0�t
]�F�]���1	��PC7ٌea�'Hr�o_�=@h��oޓ�׼z"=Z����v$��a��H�n���Pޒf�b�;*�U]���i~h�cm�1���G�X�W���j1ie�h�aLR�>����N�,H3l\�Z�/:�������ޖ��i��� �[�>��X�وA�MkZH��UYs)H�j�";p
�0[o/K�5Q��EY�~5;��z7k�
;�)��a����M��     