<template>
  <v-container fluid style="min-height: 75vh" v-if="subject" role="navigation">
    <v-list density="compact" nav role="list">
      <v-list-item @click="emit('update:modelValue', false)" role="listitem" tabindex="0">
        <template v-slot:prepend>
          <v-icon :icon="mdiClose"/>
        </template>
        <v-list-item-title>Close Menu</v-list-item-title>
      </v-list-item>
      <v-list-item to="/" exact role="listitem" tabindex="0">
        <template v-slot:prepend>
          <v-icon :icon="mdiHome"/>
        </template>
        <v-list-item-title>Home</v-list-item-title>
      </v-list-item>
      <v-list-item v-if="!isRegistered" :to="{name: 'SessionSettings'}" role="listitem" tabindex="0">
        <template v-slot:prepend>
          <v-icon :icon="mdiCog"/>
        </template>
        <v-list-item-title>Settings</v-list-item-title>
      </v-list-item>
      <v-list-item :to="{name: 'Conversations', params: {username: subject.username}}" v-if="isRegistered" role="listitem" tabindex="0">
        <template v-slot:prepend>
          <v-icon :icon="mdiEmail"/>
        </template>
        <v-list-item-title>Private Messages</v-list-item-title>
      </v-list-item>
    </v-list>
    <v-list nav density="compact" v-if="isLoggedIn && subject.artist_mode" v-model:opened="openSecond" open-strategy="multiple" role="list" tabindex="0">
      <v-divider aria-hidden="true"/>
      <v-list-item :to="{name: 'Store', params: {username: subject.username}}" role="listitem" tabindex="0">
        <template v-slot:prepend>
          <v-icon :icon="mdiStorefront"/>
        </template>
        <v-list-item-title>My Store</v-list-item-title>
      </v-list-item>
      <v-list-item :to="{name: 'CurrentSales', params: {username: subject.username}}" role="listitem" tabindex="0">
        <template v-slot:prepend>
          <v-icon :icon="mdiCashMultiple"/>
        </template>
        <v-list-item-title>Sales/Invoicing</v-list-item-title>
      </v-list-item>
      <v-list-group
          value="Reports"
          v-if="isLoggedIn && subject.is_superuser"
          nav
          role="listitem"
      >
        <template v-slot:activator="{props}">
          <v-list-item v-bind="props" tabindex="0">
            <v-list-item-title>Reports</v-list-item-title>
          </v-list-item>
        </template>
        <v-list-item :to="{name: 'Reports', params: {username: subject.username}}" role="listitem" tabindex="0">
          <template v-slot:prepend>
            <v-icon :icon="mdiChartBoxOutline"/>
          </template>
          <v-list-item-title>Financial</v-list-item-title>
        </v-list-item>
        <v-list-item :to="{name: 'TroubledDeliverables'}" role="listitem" tabindex="0">
          <template v-slot:prepend>
            <v-icon :icon="mdiAlert"/>
          </template>
          <v-list-item-title>Troubled Deliverables</v-list-item-title>
        </v-list-item>
      </v-list-group>
      <v-list-item :to="{name: 'Reports', params: {username: subject.username}}"
                   v-else-if="isLoggedIn && (subject.artist_mode || subject.is_superuser)"
                   role="listitem"
                   tabindex="0"
      >
        <template v-slot:prepend>
          <v-icon :icon="mdiChartBoxOutline"/>
        </template>
        <v-list-item-title>Reports</v-list-item-title>
      </v-list-item>
      <v-list-item :to="{name: 'TableProducts'}" v-if="isLoggedIn && subject.is_staff" role="listitem" tabindex="0">
        <template v-slot:prepend>
          <v-icon :icon="mdiStoreCogOutline"/>
        </template>
        <v-list-item-title>Table Dashboard</v-list-item-title>
      </v-list-item>
      <v-divider aria-hidden="true"/>
    </v-list>
    <v-list v-if="isStaff" nav density="compact" role="list" tabindex="0">
      <v-list-item :to="{name: 'CurrentCases', params: {username: subject.username}}" role="listitem">
        <template v-slot:prepend>
          <v-icon :icon="mdiGavel"/>
        </template>
        <v-list-item-title>Cases</v-list-item-title>
      </v-list-item>
    </v-list>
    <v-list density="compact" nav v-model:opened="openFirst" open-strategy="multiple" role="list">
      <v-list-item :to="{name: 'CurrentOrders', params: {username: subject.username}}" v-if="isLoggedIn" role="listitem" tabindex="0">
        <template v-slot:prepend>
          <v-icon :icon="mdiBasket"/>
        </template>
        <v-list-item-title>Orders</v-list-item-title>
      </v-list-item>
      <v-list-group
          value="Openings"
          v-if="isRegistered"
          nav
          role="listitem"
      >
        <template v-slot:activator="{props}">
          <v-list-item v-bind="props" tabindex="0" role="listitem">
            <v-list-item-title>Who's Open?</v-list-item-title>
          </v-list-item>
        </template>
        <v-list-item :to="{name: 'SearchProducts'}" @click.capture.stop.prevent="searchOpen({})" role="listitem" tabindex="0">
          <template v-slot:prepend>
            <v-icon class="who-is-open" :icon="mdiCity"/>
          </template>
          <v-list-item-title>All Openings</v-list-item-title>
        </v-list-item>
        <v-list-item exact :to="{name: 'SearchProducts', query: {watch_list: 'true'}}"
                     tabindex="0"
                     @click.capture.stop.prevent="searchOpen({watch_list: true})" role="listitem">
          <template v-slot:prepend>
            <v-icon class="who-is-open-watchlist" :icon="mdiStore"/>
          </template>
          <v-list-item-title>Watchlist</v-list-item-title>
        </v-list-item>
      </v-list-group>
      <v-list-item v-else exact :to="{name: 'SearchProducts'}" @click.capture.stop.prevent="searchOpen({})" role="listitem" tabindex="0">
        <template v-slot:prepend>
          <v-icon class="who-is-open" :icon="mdiStore"/>
        </template>
        <v-list-item-title>Who's Open?</v-list-item-title>
      </v-list-item>
      <v-list-group
          nav
          v-if="isRegistered"
          value="Art"
          role="listitem"
      >
        <template v-slot:activator="{props}">
          <v-list-item v-bind="props" tabindex="0" role="listitem">
            <v-list-item-title>Recent Art</v-list-item-title>
          </v-list-item>
        </template>
        <v-list-item :exact="true" :to="{name: 'SearchSubmissions'}"
                     @click.capture.stop.prevent="searchSubmissions({})" role="listitem" tabindex="0">
          <template v-slot:prepend>
            <v-icon class="recent-art" :icon="mdiImageMultiple"/>
          </template>
          <v-list-item-title>All Submissions</v-list-item-title>
        </v-list-item>
        <v-list-item :exact="true" :to="{name: 'SearchSubmissions', query: {watch_list: 'true'}}"
                     @click.capture.stop.prevent="searchSubmissions({watch_list: true})" role="listitem" tabindex="0">
          <template v-slot:prepend>
            <v-icon class="recent-art-watchlist" :icon="mdiEye"/>
          </template>
          <v-list-item-title>Watchlist</v-list-item-title>
        </v-list-item>
      </v-list-group>
      <v-list-item v-else :to="{name: 'SearchSubmissions'}" @click.capture.stop.prevent="searchSubmissions({})" role="listitem" tabindex="0">
        <template v-slot:prepend>
          <v-icon class="recent-art" :icon="mdiImageMultiple"/>
        </template>
        <v-list-item-title>Recent Art</v-list-item-title>
      </v-list-item>
      <v-list-item :to="{name: 'LinksAndStats', params: {username: subject.username}}" v-if="isRegistered" role="listitem" tabindex="0">
        <template v-slot:prepend>
          <v-icon :icon="mdiStar"/>
        </template>
        <v-list-item-title>
          Extras!
        </v-list-item-title>
      </v-list-item>
      <v-list-item :to="{name: 'Upgrade', params: {username: subject.username}}" v-if="isRegistered && !embedded" role="listitem" tabindex="0">
        <template v-slot:prepend>
          <v-icon :icon="mdiArrowUp"/>
        </template>
        <v-list-item-title>
          Upgrade
        </v-list-item-title>
      </v-list-item>
      <v-list-item class="hidden-sm-and-up" v-if="!showSfwToggle" role="listitem" tabindex="0">
        <ac-patch-field
            field-type="v-switch"
            :patcher="sfwMode"
            :save-indicator="false"
            label="SFW Mode"
            color="primary"
        />
      </v-list-item>
    </v-list>
    <v-divider aria-hidden="true"/>
    <v-list nav density="compact" role="list">
      <v-list-group v-if="isRegistered"
                    prepend-icon="mdi-cog" value="Settings" role="listitem">
        <template v-slot:activator="{props}">
          <v-list-item v-bind="props" tabindex="0">
            <v-list-item-title>Settings</v-list-item-title>
          </v-list-item>
        </template>
        <ac-setting-nav :username="subject.username" :nested="true"/>
      </v-list-group>
      <v-list-item :to="{name: 'About'}" v-if="!embedded" tabindex="0" role="listitem">
        <template v-slot:prepend>
          <v-icon :icon="mdiForum"/>
        </template>
        <v-list-item-title>FAQ</v-list-item-title>
      </v-list-item>
      <v-list-item @click.prevent="logout()" v-if="isRegistered && !embedded" tabindex="0" role="listitem">
        <template v-slot:prepend>
          <v-icon class="logout-button" :icon="mdiLogout"/>
        </template>
        <v-list-item-title>Log out</v-list-item-title>
      </v-list-item>
      <v-list-item class="mt-3" :to="{name: 'Policies'}" v-if="!embedded" tabindex="0"  role="listitem">
        <template v-slot:prepend>
          <v-icon :icon="mdiInformation"/>
        </template>
        <v-list-item-title>Privacy and Legal</v-list-item-title>
      </v-list-item>
    </v-list>
  </v-container>
</template>

<script setup lang="ts">
import AcSettingNav from '@/components/navigation/AcSettingNav.vue'
import {ProfileController} from '@/store/profiles/controller.ts'
import AcPatchField from '@/components/fields/AcPatchField.vue'
import {artCall, makeQueryParams, setViewer} from '@/lib/lib.ts'
import {RawData} from '@/store/forms/types/RawData.ts'
import {User} from '@/store/profiles/types/User.ts'
import {AnonUser} from '@/store/profiles/types/AnonUser.ts'
import {computed, ref} from 'vue'
import {useForm} from '@/store/forms/hooks.ts'
import {useRouter} from 'vue-router'
import {
  mdiAlert,
  mdiArrowUp, mdiBasket, mdiCashMultiple, mdiChartBoxOutline,
  mdiCity, mdiClose, mdiCog, mdiEmail,
  mdiEye,
  mdiForum, mdiGavel, mdiHome,
  mdiImageMultiple,
  mdiInformation,
  mdiLogout,
  mdiStar,
  mdiStore, mdiStoreCogOutline, mdiStorefront,
} from '@mdi/js'
import {useViewer} from '@/mixins/viewer.ts'

declare interface AcNavLinksProps {
  modelValue: boolean|null,
  subjectHandler: ProfileController,
  isRegistered: boolean,
  isLoggedIn: boolean,
  embedded?: boolean,
  isStaff: boolean,
  isSuperuser: boolean,
}

const props = withDefaults(defineProps<AcNavLinksProps>(), {embedded: false})
const router = useRouter()
const {viewerHandler} = useViewer()

const openFirst = ref(['Openings', 'Art'])
const openSecond = ref(['Reports'])

const emit = defineEmits<{'update:modelValue': [boolean|null]}>()

const subject = computed(() => props.subjectHandler.user.x)
const sfwMode = computed(() => props.subjectHandler.user.patchers.sfw_mode)
const showSfwToggle = computed(() => props.embedded && subject.value && (subject.value as User).rating > 0)

const searchForm = useForm('search')


const searchOpen = (data: RawData) => {
  searchReplace(data)
  router.push({
    name: 'SearchProducts',
    query: makeQueryParams(searchForm.rawData),
  })
}

const searchReplace = (data: RawData) => {
  searchForm.reset()
  for (const key of Object.keys(data)) {
    searchForm.fields[key].update(data[key])
  }
}

const searchSubmissions = (data: RawData) => {
  searchReplace(data)
  router.push({
    name: 'SearchSubmissions',
    query: makeQueryParams(searchForm.rawData),
  })
}

const logout = () => {
  artCall({
    url: '/api/profiles/logout/',
    method: 'post',
  }).then((newUser: AnonUser) => {
    viewerHandler.user.setX(newUser)
    router.push({name: 'Home'})
    emit('update:modelValue', null)
  })
}
</script>
