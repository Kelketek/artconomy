<template>
  <v-container fluid style="min-height: 75vh" v-if="subject">
    <v-list density="compact" nav >
      <v-list-item @click="$emit('update:modelValue', false)">
        <template v-slot:prepend>
          <v-icon icon="mdi-close"/>
        </template>
        <v-list-item-title>Close Menu</v-list-item-title>
      </v-list-item>
      <v-list-item to="/" exact>
        <template v-slot:prepend>
          <v-icon icon="mdi-home"/>
        </template>
        <v-list-item-title>Home</v-list-item-title>
      </v-list-item>
      <v-list-item v-if="!isRegistered" :to="{name: 'SessionSettings'}">
        <template v-slot:prepend>
          <v-icon icon="mdi-cog"/>
        </template>
        <v-list-item-title>Settings</v-list-item-title>
      </v-list-item>
      <v-list-item :to="{name: 'Conversations', params: {username: subject.username}}" v-if="isRegistered">
        <template v-slot:prepend>
          <v-icon icon="mdi-email"/>
        </template>
        <v-list-item-title>Private Messages</v-list-item-title>
      </v-list-item>
    </v-list>
    <v-list nav density="compact" v-if="isLoggedIn && subject.artist_mode" v-model:opened="openSecond" open-strategy="multiple">
      <v-divider/>
      <v-list-item :to="{name: 'Store', params: {username: subject.username}}">
        <template v-slot:prepend>
          <v-icon icon="mdi-storefront"/>
        </template>
        <v-list-item-title>My Store</v-list-item-title>
      </v-list-item>
      <v-list-item :to="{name: 'CurrentSales', params: {username: subject.username}}">
        <template v-slot:prepend>
          <v-icon icon="mdi-cash-multiple"/>
        </template>
        <v-list-item-title>Sales/Invoicing</v-list-item-title>
      </v-list-item>
      <v-list-group
          value="Reports"
          v-if="isLoggedIn && subject.is_superuser"
          nav
      >
        <template v-slot:activator="{props}">
          <v-list-item v-bind="props">
            <v-list-item-title>Reports</v-list-item-title>
          </v-list-item>
        </template>
        <v-list-item :to="{name: 'Reports', params: {username: subject.username}}">
          <template v-slot:prepend>
            <v-icon icon="mdi-chart-box-outline"/>
          </template>
          <v-list-item-title>Financial</v-list-item-title>
        </v-list-item>
        <v-list-item :to="{name: 'TroubledDeliverables'}">
          <template v-slot:prepend>
            <v-icon icon="mdi-alert"/>
          </template>
          <v-list-item-title>Troubled Deliverables</v-list-item-title>
        </v-list-item>
      </v-list-group>
      <v-list-item :to="{name: 'Reports', params: {username: subject.username}}"
                   v-else-if="isLoggedIn && (subject.artist_mode || subject.is_superuser)">
        <template v-slot:prepend>
          <v-icon icon="mdi-chart-box-outline"/>
        </template>
        <v-list-item-title>Reports</v-list-item-title>
      </v-list-item>
      <v-list-item :to="{name: 'TableProducts'}" v-if="isLoggedIn && subject.is_staff">
        <template v-slot:prepend>
          <v-icon icon="mdi-store-cog-outline"/>
        </template>
        <v-list-item-title>Table Dashboard</v-list-item-title>
      </v-list-item>
      <v-divider/>
    </v-list>
    <v-list v-if="isStaff" nav density="compact">
      <v-list-item :to="{name: 'CurrentCases', params: {username: subject.username}}">
        <template v-slot:prepend>
          <v-icon icon="mdi-gavel"/>
        </template>
        <v-list-item-title>Cases</v-list-item-title>
      </v-list-item>
    </v-list>
    <v-list density="compact" nav v-model:opened="openFirst" open-strategy="multiple">
      <v-list-item :to="{name: 'CurrentOrders', params: {username: subject.username}}" v-if="isLoggedIn">
        <template v-slot:prepend>
          <v-icon icon="mdi-basket"/>
        </template>
        <v-list-item-title>Orders</v-list-item-title>
      </v-list-item>
      <v-list-group
          value="Openings"
          v-if="isRegistered"
          nav
      >
        <template v-slot:activator="{props}">
          <v-list-item v-bind="props">
            <v-list-item-title>Who's Open?</v-list-item-title>
          </v-list-item>
        </template>
        <v-list-item :to="{name: 'SearchProducts'}" @click.capture.stop.prevent="searchOpen({})">
          <template v-slot:prepend>
            <v-icon class="who-is-open" icon="mdi-city"/>
          </template>
          <v-list-item-title>All Openings</v-list-item-title>
        </v-list-item>
        <v-list-item exact :to="{name: 'SearchProducts', query: {watch_list: 'true'}}"
                     @click.capture.stop.prevent="searchOpen({watch_list: true})">
          <template v-slot:prepend>
            <v-icon class="who-is-open-watchlist" icon="mdi-store"/>
          </template>
          <v-list-item-title>Watchlist</v-list-item-title>
        </v-list-item>
      </v-list-group>
      <v-list-item v-else exact :to="{name: 'SearchProducts'}" @click.capture.stop.prevent="searchOpen({})">
        <template v-slot:prepend>
          <v-icon class="who-is-open" icon="mdi-store"/>
        </template>
        <v-list-item-title>Who's Open?</v-list-item-title>
      </v-list-item>
      <v-list-group
          nav
          v-if="isRegistered"
          value="Art"
      >
        <template v-slot:activator="{props}">
          <v-list-item v-bind="props">
            <v-list-item-title>Recent Art</v-list-item-title>
          </v-list-item>
        </template>
        <v-list-item :exact="true" :to="{name: 'SearchSubmissions'}"
                     @click.capture.stop.prevent="searchSubmissions({})">
          <template v-slot:prepend>
            <v-icon class="recent-art" icon="mdi-image-multiple"/>
          </template>
          <v-list-item-title>All Submissions</v-list-item-title>
        </v-list-item>
        <v-list-item :exact="true" :to="{name: 'SearchSubmissions', query: {watch_list: 'true'}}"
                     @click.capture.stop.prevent="searchSubmissions({watch_list: true})">
          <template v-slot:prepend>
            <v-icon class="recent-art-watchlist" icon="mdi-eye"/>
          </template>
          <v-list-item-title>Watchlist</v-list-item-title>
        </v-list-item>
      </v-list-group>
      <v-list-item v-else :to="{name: 'SearchSubmissions'}" @click.capture.stop.prevent="searchSubmissions({})">
        <template v-slot:prepend>
          <v-icon class="recent-art" icon="mdi-image-multiple"/>
        </template>
        <v-list-item-title>Recent Art</v-list-item-title>
      </v-list-item>
      <v-list-item :to="{name: 'LinksAndStats', params: {username: subject.username}}" v-if="isRegistered">
        <template v-slot:prepend>
          <v-icon icon="mdi-star"/>
        </template>
        <v-list-item-title>
          Extras!
        </v-list-item-title>
      </v-list-item>
      <v-list-item :to="{name: 'Upgrade', params: {username: subject.username}}" v-if="isRegistered && !embedded">
        <template v-slot:prepend>
          <v-icon icon="mdi-arrow-up"/>
        </template>
        <v-list-item-title>
          Upgrade
        </v-list-item-title>
      </v-list-item>
      <v-list-item class="hidden-sm-and-up" v-if="!showSfwToggle">
        <ac-patch-field
            field-type="v-switch"
            :patcher="sfwMode"
            :save-indicator="false"
            label="SFW Mode"
            color="primary"
        />
      </v-list-item>
    </v-list>
    <v-divider></v-divider>
    <v-list nav density="compact">
      <v-list-group :to="{name: 'Options', params: {'username': subject.username}}" v-if="isRegistered"
                    prepend-icon="mdi-cog" value="Settings">
        <template v-slot:activator="{props}">
          <v-list-item v-bind="props">
            <v-list-item-title>Settings</v-list-item-title>
          </v-list-item>
        </template>
        <ac-setting-nav :username="subject.username" :nested="true"/>
      </v-list-group>
      <v-list-item :to="{name: 'About'}" v-if="!embedded">
        <template v-slot:prepend>
          <v-icon icon="mdi-forum"/>
        </template>
        <v-list-item-title>FAQ</v-list-item-title>
      </v-list-item>
      <v-list-item @click.prevent="logout()" v-if="isRegistered && !embedded">
        <template v-slot:prepend>
          <v-icon class="logout-button" icon="mdi-logout"/>
        </template>
        <v-list-item-title>Log out</v-list-item-title>
      </v-list-item>
      <v-list-item class="mt-3" :to="{name: 'Policies'}" v-if="!embedded">
        <template v-slot:prepend>
          <v-icon icon="mdi-information"/>
        </template>
        <v-list-item-title>Privacy and Legal</v-list-item-title>
      </v-list-item>
    </v-list>
  </v-container>
</template>

<script lang="ts">
import {Component, Prop, toNative} from 'vue-facing-decorator'
import AcSettingNav from '@/components/navigation/AcSettingNav.vue'
import {FormController} from '@/store/forms/form-controller.ts'
import {AnyUser, ProfileController} from '@/store/profiles/controller.ts'
import AcPatchField from '@/components/fields/AcPatchField.vue'
import {artCall, ArtVue, makeQueryParams} from '@/lib/lib.ts'
import {RawData} from '@/store/forms/types/RawData.ts'
import {User} from '@/store/profiles/types/User.ts'
import {AnonUser} from '@/store/profiles/types/AnonUser.ts'

@Component({
  components: {
    AcPatchField,
    AcSettingNav,
  },
  emits: ['update:modelValue'],
})
class AcNavDrawer extends ArtVue {
  public searchForm: FormController = null as unknown as FormController
  @Prop({required: true})
  public modelValue!: boolean

  @Prop({required: true})
  public subjectHandler!: ProfileController

  @Prop({required: true})
  public isRegistered!: boolean

  @Prop({required: true})
  public isLoggedIn!: boolean

  @Prop({default: false})
  public embedded!: boolean

  @Prop({required: true})
  public isStaff!: boolean

  @Prop({required: true})
  public isSuperuser!: boolean

  public openFirst = ['Openings', 'Art']
  public openSecond = ['Reports']

  public get subject() {
    return this.subjectHandler.user.x
  }

  public get sfwMode() {
    return this.subjectHandler.user.patchers.sfw_mode
  }

  public get showSfwToggle() {
    return this.embedded && this.subject && (this.subject as User).rating > 0
  }

  public searchOpen(data: RawData) {
    this.searchReplace(data)
    this.$router.push({
      name: 'SearchProducts',
      query: makeQueryParams(this.searchForm.rawData),
    })
  }

  public searchReplace(data: RawData) {
    this.searchForm.reset()
    for (const key of Object.keys(data)) {
      this.searchForm.fields[key].update(data[key])
    }
  }

  public searchSubmissions(data: RawData) {
    this.searchReplace(data)
    this.$router.push({
      name: 'SearchSubmissions',
      query: makeQueryParams(this.searchForm.rawData),
    })
  }

  public logout() {
    artCall({
      url: '/api/profiles/logout/',
      method: 'post',
    }).then((newUser: AnonUser) => {
      this.subjectHandler.user.setX(newUser)
      this.$router.push({name: 'Home'})
      this.$emit('update:modelValue', null)
    })
  }

  public created() {
    this.searchForm = this.$getForm('search')
    // @ts-ignore
    window.links = this
  }
}

export default toNative(AcNavDrawer)
</script>
